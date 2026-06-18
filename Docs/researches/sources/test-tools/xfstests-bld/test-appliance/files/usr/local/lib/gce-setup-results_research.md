# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-setup-results

Purpose: initializes `/results` for a test run.

Important flow: create `/results`, touch `runtests.log`, copy `/var/www/cmdline`, copy hooks and `/proc/config.gz` if available, write `uname -r` and `$TESTRUNID`, fetch `check-time.tar.gz` from GCS, unpack it in `/results`, and move `check.time.*` files into per-results directories with `check.time` names.

State and dependencies: `/results` tree, `kernel_version`, `testrunid`, unpacked historical timing files. Depends on `gcs_cp`, tar, and environment variables.

Integration points: run by `gce-setup` before tests; shutdown and LTM result aggregation consume `/results` files.

Risks and test signals: missing check-time tarball is tolerated only through redirected command behavior; subsequent tar may fail if `/tmp/check-time.tar.gz` is absent. Tests should check initialization with and without optional hooks/config/timing files.
