# sources/security-integrity/selinux/scripts/run-scan-build
# sources/security-integrity/selinux/scripts/run-scan-build

Purpose: runs clang static analyzer over a full SELinux build/install.

Important APIs and control flow: sets `CC=clang`, `SCAN_BUILD`, output directory, optional temporary `DESTDIR`, staged library/binary/Python/Ruby paths, Debian Python layout variable, runs `make clean distclean`, then `scan-build -analyze-headers` around a large install/build target with fortified CFLAGS. On success it removes the temporary DESTDIR after making `newrole` writable.

State and persistence: writes analyzer reports under `scripts/output-scan-build`, creates/removes DESTDIR, and builds repository artifacts.

Dependencies and integration points: developer/CI diagnostic helper using clang scan-build, make, Python, Ruby, and the whole SELinux build system.

Risks and test signals: broad build can be slow and destructive to local build artifacts due to clean/distclean. Analyzer output is the main signal; no self-test.
