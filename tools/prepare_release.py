#!/usr/bin/env python3
"""Build a fresh MPI rehearsal folder and verify the local public routes."""

import argparse
from html.parser import HTMLParser
from pathlib import Path
import posixpath
import re
import shutil
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET

SOURCE = Path(__file__).resolve().parents[1]
DOMAIN = "https://www.modusponensinstitute.com"
STAGING = "https://ethicscomp101.github.io/mpi-site-staging/"
PUBLIC_DIRS = {
    "account", "blog", "category", "event-details-registration", "files",
    "images", "plans-pricing", "post", "pricing-plans", "profile", "service-page",
}
PUBLIC_TYPES = {".html", ".css", ".js", ".jpg", ".jpeg", ".png", ".webp", ".svg", ".pdf", ".ico"}
PRIVATE_SEARCH = {"404.html", "tournament-day.html"}
EXTERNAL_REDIRECTS = {
    "copy-of-olympiads.html": "https://globalaidebates.com/",
    "globalaidebates.html": "https://globalaidebates.com/",
}
ROBOTS_TAG = re.compile(r'<meta name="robots" content="[^"]*"\s*/?>\s*', re.I)
CANONICAL_TAG = re.compile(r'<link rel="canonical" href="[^"]*"\s*/?>\s*', re.I)
REFRESH = re.compile(r'<meta\b[^>]+http-equiv="refresh"[^>]+content="[^"]*?url=([^"]+)"', re.I)
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


class Links(HTMLParser):
    def __init__(self, document):
        super().__init__(convert_charrefs=True)
        self.references = []
        self.ids = set()
        self.feed(document)

    def handle_starttag(self, tag, attributes):
        values = dict(attributes)
        if values.get("id"):
            self.ids.add(values["id"])
        if values.get("name") and tag == "a":
            self.ids.add(values["name"])
        if tag == "base" or values.get("rel") == "canonical":
            return
        for attr in ("href", "src", "poster"):
            if values.get(attr):
                self.references.append(values[attr])
        if values.get("srcset"):
            self.references.extend(value.strip().split()[0] for value in values["srcset"].split(",") if value.strip())


def resolve_path(path, output):
    path = posixpath.normpath(unquote(path)).lstrip("/")
    if path == ".":
        path = "index.html"
    if path == ".." or path.startswith("../"):
        return None
    for name in (path, path + ".html", path + "/index.html"):
        if (output / name).is_file():
            return name
    return None


def local_path(origin, url):
    parts = urlsplit(url)
    if parts.netloc:
        return None, ""
    if parts.scheme or parts.path.startswith("//"):
        return None, ""
    if not parts.path:
        return origin, parts.fragment
    # The 404 template sets a base at the website root.
    if parts.path.startswith("/") or origin == "404.html":
        return parts.path, parts.fragment
    return posixpath.join(posixpath.dirname(origin), parts.path), parts.fragment


def copy_public(output, release_policy):
    included = []
    redirects = {}
    for source in sorted(SOURCE.rglob("*")):
        rel = source.relative_to(SOURCE)
        if len(rel.parts) > 1 and rel.parts[0] not in PUBLIC_DIRS:
            continue
        if not source.is_file() or source.suffix not in PUBLIC_TYPES:
            continue
        dest = output / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix != ".html":
            shutil.copyfile(source, dest)
            continue
        document = source.read_text().replace(STAGING, "/") if release_policy else source.read_text()
        refresh = REFRESH.search(document)
        if refresh:
            redirects[rel.as_posix()] = refresh[1]
        else:
            route = rel.as_posix()
            canonical = DOMAIN + ("/" if route == "index.html" else "/" + route.removesuffix(".html"))
            document = CANONICAL_TAG.sub("", document)
            document = ROBOTS_TAG.sub("", document)
            meta = f'<link rel="canonical" href="{canonical}">\n'
            if route in PRIVATE_SEARCH or not release_policy:
                meta += '<meta name="robots" content="noindex, nofollow">\n'
            if route not in PRIVATE_SEARCH:
                included.append(canonical)
            if "</head>" not in document:
                raise ValueError(f"Document has no head: {route}")
            document = document.replace("</head>", meta + "</head>", 1)
        dest.write_text(document)

    ET.register_namespace("", SITEMAP_NS)
    sitemap = ET.Element(f"{{{SITEMAP_NS}}}urlset")
    for url in sorted(included):
        page = ET.SubElement(sitemap, f"{{{SITEMAP_NS}}}url")
        ET.SubElement(page, f"{{{SITEMAP_NS}}}loc").text = url
    ET.indent(sitemap)
    ET.ElementTree(sitemap).write(output / "sitemap.xml", encoding="utf-8", xml_declaration=True)
    robots = "User-agent: *\nDisallow: /\n"
    if release_policy:
        robots = f"User-agent: *\nAllow: /\nDisallow: /tournament-day\nSitemap: {DOMAIN}/sitemap.xml\n"
    (output / "robots.txt").write_text(robots)
    (output / ".nojekyll").touch()
    return included, redirects


def validate(output, redirects):
    documents = {
        page.relative_to(output).as_posix(): Links(page.read_text())
        for page in output.rglob("*.html")
    }
    errors = set()
    for file, markup in documents.items():
        for reference in set(markup.references):
            path, fragment = local_path(file, reference)
            if path is None:
                continue
            target = resolve_path(path, output)
            if target is None:
                errors.add((file, reference, "missing target"))
            elif fragment and target in documents and unquote(fragment) not in documents[target].ids:
                errors.add((file, reference, "missing fragment"))

    for file, destination in redirects.items():
        visited = {file}
        origin = file
        while True:
            if EXTERNAL_REDIRECTS.get(origin) == destination:
                break
            path, _ = local_path(origin, destination)
            target = resolve_path(path, output) if path is not None else None
            if not target:
                errors.add((file, destination, "redirect has no local destination"))
                break
            if target in visited:
                errors.add((file, destination, "redirect loop"))
                break
            if target not in redirects:
                break
            visited.add(target)
            origin, destination = target, redirects[target]
    return documents, sorted(errors)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--release-policy", action="store_true",
                        help="Rehearse production robots and canonicals in the local output.")
    args = parser.parse_args()
    output = args.output.resolve()
    if output == SOURCE or output.is_relative_to(SOURCE):
        parser.error("Use an output path outside the staging source.")
    if output.exists():
        parser.error("Use a new output path. This tool never overwrites an earlier build.")
    output.mkdir(parents=True)
    sitemap, redirects = copy_public(output, args.release_policy)
    documents, errors = validate(output, redirects)
    print(f"{len(documents)} HTML routes, {len(redirects)} redirect stubs, {len(sitemap)} sitemap entries")
    for issue in errors:
        print(" | ".join(issue))
    if errors:
        raise SystemExit(1)
    print(f"Verified local files, fragments and redirect targets in {output}")


if __name__ == "__main__":
    main()
