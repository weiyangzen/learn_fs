# sources/sync-backup/unison/dev/ktrace-netbsd

Purpose: NetBSD developer script to trace executable/path usage during Unison build, install, and clean phases.

Important flow: validates it is run at the Unison source top level by checking `src/Makefile.OCaml`, runs `make clean`, removes old `ktrace*`, traces `make`, traces `make DESTDIR=/tmp/U install`, traces `make clean`, dumps traces with `kdump`, extracts `NAMI` path records, normalizes `/usr` and `/pkg`, filters bin/sbin paths, counts unique entries, and writes `NAMI.txt`.

State/persistence: creates `ktrace-make.txt`, `ktrace-install.txt`, `ktrace-clean.txt`, `NAMI.txt`, and `/tmp/U`. It intentionally avoids deleting `/tmp/U`.

Dependencies/integration: NetBSD `ktrace`, `kdump`, `egrep`, `awk`, `sed`, `sort`, `uniq`, and a working Unison make build.

Risks: NetBSD-specific and intentionally not portable. The path normalization is heuristic and focused on bin-like directories. `/tmp/U` may already exist or accumulate files.

Test signals: useful output is `NAMI.txt`, a counted list of command paths observed during build/install/clean.
