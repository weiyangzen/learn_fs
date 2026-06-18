# File Research: sources/virtualization/nvme-cli/Makefile

- Purpose: convenience wrapper around Meson for common developer/package tasks.
- Targets: build, clean/purge, install/uninstall, update-accessors, dist, test, test-strict, rpm, debug, static, checkpatch, and checkpatch-diff.
- Build behavior: creates `.build` with `meson setup`; `PLUGINS` maps to `-Dplugins=`.
- Static target: configures release static build with fallback wraps and disables keyutils, liburing, Python, OpenSSL, tests, and examples.
- Checkpatch: downloads kernel `checkpatch.pl` to `/tmp/checkpatch.pl` and checks either commit range or local diff/untracked files.
