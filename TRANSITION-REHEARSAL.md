# MPI design and Wix transition rehearsal

Prepared 21 November 2026 for review before porting. The redesign is on the local `mpi-full-design` branch of `EthicsComp101/mpi-site-staging`. The intended production repository is `EthicsComp101/mpi-site`. It exists and the connected GitHub account has admin access. GitHub Pages is currently disabled on that repository.

## What to review

- Start on Home and try **Start a team** and **Find an event**. Homepage and competition-list events come from the same calendar, and the events link straight to their details.
- Check the calendar with the age and region of a real team. Compare the organiser’s details before registering. Archived events are available with **Include past events**.
- On Resources, open the handbook, find a case set and start the match timer. Review entry details and sample work on Case Writing Prize.
- Check Classes and Tutoring, Junior Ethics, Past Results and Fund Your Team. The last page labels saved grant information so it can be checked with each funder.
- On Tournament Day, participants can reach the day-of instructions and timer. The public page links to MPI contact for organiser access. The previous embedded organiser tool is excluded from this draft.

## What passed

- All 63 public routes from the seven current Wix child sitemaps map to an HTML page or a redirect stub. All 24 live Wix Redirect Manager source paths are present. See [the route inventory](tools/wix-route-inventory.csv) for the destination beside each source. The group payment redirect still needs testing with any active checkout suffixes.
- The local release rehearsal contains 103 HTML routes, including 50 redirect stubs, and 51 indexable sitemap entries. The preparation tool checks internal paths, HTML fragments and redirect targets. GitHub Pages currently serves both the extensionless and `.html` forms of the staging Resources URL.
- Chromium checks covered 16 pages at 1440, 768 and 375 pixels. The functional checks exercised the mobile menu with the keyboard, homepage event links, event filtering and archives, handbook links and keyboard access, the match timer, and grant search.
- Public requests loaded the class enquiry, planning-call calendar, representative event registration pages, Case Writing Prize overview, newsletter script and both existing Wix booking service pages. A page loading confirms the link. Submission, notification, booking fulfilment and payment require separate acceptance checks.
- Public DNS resolves the apex web address to Wix A records `185.230.63.107`, `185.230.63.171` and `185.230.63.186`. The `www` CNAME is `cdn3.wixdns.net`. Wix is authoritative and Google Workspace MX records are in place. The existing operations folder contains the fuller `DNS-BEFORE.md` baseline. Save an updated complete export directly from Wix for the final rollback copy.

## Items to close before switching

| Workstream | Current position | Acceptance |
|---|---|---|
| Design and calendar | Full design is locally browsable. The Spring Invitational’s age and end time disagree between the original staging copy and the organiser, and the prize page and calendar described different rounds. | Review the design. Confirm the official ages, schedule and registration deadline for the Spring Invitational. Confirm the Case Writing Prize round, deadline and entry URL. |
| Wix bookings, billing and plans | Wix Bookings and Wix Pricing Plans are installed. The local route stubs for the two Wix services lead to Classes and Tutoring. The Wix site context returned the custom domain, so its fallback host is still unverified. | Verify a Wix-managed URL that remains usable after the custom domain moves, or approve an enquiry bridge for each live service. Check existing bookings and active billing in Wix. Test the entire booking and payment path with authorised test data. Keep Wix billing and existing customer access available. |
| Forms and newsletters | Class enquiry still uses Jotform. Newsletters uses the existing Sender form on its own page. | Verify an approved test reaches the intended owner, thank-you URLs work, and an approved test newsletter address subscribes, confirms and unsubscribes. Export contacts and subscriptions privately with consent and unsubscribe status intact before exiting Wix. |
| Tournament Day | The public participant page is in the candidate. | Confirm an authenticated organiser URL with the event organiser and test access for both authorised and unauthorised viewers before replacing any active workflow. |
| Production hosting and DNS | The build is ready to rehearse locally. GitHub Pages is disabled on the production repository. | After review, publish the reviewed artifact to the production repository and verify it at its GitHub URL before configuring the production domain and changing the web records. Final approval is required for the switch. |
| Analytics and search | Preview retains staging search restrictions. The production rehearsal generates canonical URLs and a public sitemap while excluding redirect stubs and Tournament Day. | Verify analytics ownership and test the real conversion signals. After cutover, check both domain variants, the sitemap, high-traffic legacy URLs and Search Console. |

## Rebuild or rehearse

From the design worktree, run `python3 tools/prepare_release.py --output /tmp/mpi-preview-new` to build a fresh local preview. To rehearse the production search policy, use a fresh output path and add `--release-policy`. Serve the output locally for review. The tool creates a new directory and rejects an existing output. It writes no CNAME and excludes the experiments, tools and Git files.

## Switch and rollback

After the table is complete and Archie authorises the switch, record the approved branch and build, export the current DNS zone, and schedule a quiet window. Keep the Wix site and registrar active, including the Google Workspace billing and existing mail records. Verify ownership and configure the custom domain on the production GitHub Pages repository before editing the Wix web records. Use the current values in GitHub’s instructions, then validate HTTPS for both `www` and the apex. Keep MX, SPF, DKIM, DMARC and other mail records as recorded. [GitHub Pages custom-domain instructions](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)

Smoke test Home, Resources, Case Writing Prize, Event Calendar, registration, class contact, newsletter, active booking routes and the organiser link. Check both mailboxes inbound and outbound using an authorised test. Verify old URLs and campaign links retain useful destinations. If the public site, booking, or mail checks fail, restore the recorded Wix web DNS entries and confirm traffic returns to Wix. Keep Wix available throughout the rollback window.

Use the existing operations log as the place to record cutover time, approver, test results, DNS propagation and any rollback. [Wix contact export instructions](https://support.wix.com/en/article/wix-contacts-exporting-your-contacts)
