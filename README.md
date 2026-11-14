# MPI staging

Serve this directory as /mpi-site-staging/. Relative internal links preserve that base path. Capture/build scripts are in /Users/archiestapleton/Documents/Codex/mpi-r2*.cjs. Live source captures and audit are in the parent directory. Do not run the round-one generic builder.

Rebuild scripts, in order: `mpi-r2.cjs` captures and assembles live sections; `mpi-r2-finish.cjs` restores native blog content and image attributes; `mpi-r2-repair.cjs` preserves interactive research templates and links hosted forms/bookings; `mpi-r2-count.cjs` measures comparable content; `mpi-r2-tidy.cjs` restores the gallery and validates links; `mpi-r2-assets.cjs` repairs encoded asset references; `mpi-r2-report.cjs` generates audit tables. Run using the bundled Node runtime with its node_modules on NODE_PATH. The browser executable path is specified in the scripts. The final handoff notes in SUMMARY.md contain additional manual QA results and should be preserved when regenerating reports.
