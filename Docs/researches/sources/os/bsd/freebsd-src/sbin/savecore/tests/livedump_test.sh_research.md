# File Research: sources/os/bsd/freebsd-src/sbin/savecore/tests/livedump_test.sh

## Summary
ATF shell test validating live dump integrity by comparing module-list output from the generated live core with the running system.

## Main Elements
- Requires root and `kgdb`.
- Runs `savecore -L .` and expects live-dump logging on stderr.
- Skips when debug symbols for the running kernel are unavailable.
- Creates a small gdb script that walks `linker_files`.
- Runs `kgdb` against `livecore.0`, filters gdb prompt noise, and compares output with `kldstat`.

## Dependencies And Integration
Uses `savecore`, `sysctl kern.bootfile`, `/usr/lib/debug`, `kgdb`, `kldstat`, `sed`, `diff`, and ATF helpers.

## Research Notes
The test is sensitive to concurrent kernel module loads, which is why the Makefile marks it exclusive.
