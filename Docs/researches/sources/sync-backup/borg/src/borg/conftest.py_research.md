# sources/sync-backup/borg/src/borg/conftest.py

Purpose: configures Borg's pytest environment, isolates test state, cleans stale FUSE mountpoints, reports platform capability headers, and provides reusable archiver fixtures.

Important APIs: `pytest_sessionstart`/`pytest_sessionfinish` sweep stale `mountpoint` directories under pytest temp roots. `clean_env` autouse fixture removes most `BORG_*` environment variables, sets isolated `BORG_BASE_DIR`, weakens KDF for tests, and configures flat storage. `set_env_variables` sets confirmation/passphrase/selftest values. `backup_files` creates a small fixture tree. `ArchiverSetup` records paths and execution kind. `archiver`, `remote_archiver`, and `binary_archiver` fixtures create local/rest/binary test setups with keys/cache/input/output paths.

Control flow and state: test sessions perform best-effort FUSE cleanup before and after runs in the main process only. Each test gets a temporary base directory and archiver workspace, with environment variables pointing to isolated keys/cache directories. Cleanup handles BSD flags when removing temp trees.

Dependencies and integration: imports Borg logging setup early, `Archiver`, testsuite capability probes, `BORG_EXES`, platform fakeroot detection, and `helpers.umount`. Pytest assertion rewrite is registered for `borg.testsuite`.

Risks: autouse environment wiping can hide bugs dependent on user environment but is necessary for reproducibility. FUSE cleanup walks temp directories and best-effort unmounts paths named `mountpoint`; incorrect detection could miss or attempt stale resources. `BORG_TESTONLY_WEAKEN_KDF=1` must never leak into production contexts.

Test signals: this file is test infrastructure; validate by running representative local, remote, and binary archiver tests, plus interrupted FUSE cleanup scenarios and xdist session behavior.
