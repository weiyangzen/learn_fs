## sources/security-integrity/ecryptfs-utils/tests/kernel/mmap-dir/test.c

Purpose: C negative test for `mmap()` on an eCryptfs directory. It checks the fix for LP 400443: mmaping a directory should fail with `ENODEV` instead of returning an address that later SIGBUSes.

Important APIs and functions: `main`, `open` on `argv[1]/.`, `mmap(PROT_READ, MAP_PRIVATE)`, `munmap`, `errno` checks. Control flow opens the directory, attempts a 4096-byte mmap, closes fd, fails if mmap succeeds, and fails if the errno is not `ENODEV`.

State and persistence: No persistent writes; reads directory metadata only. Dependencies are Linux directory-file behavior and eCryptfs VFS mmap handlers. Integration is via `mmap-dir.sh`. Risks include kernel/filesystem errno differences; the test is intentionally strict about `ENODEV`, so a generic failure with a different errno is treated as a regression. Test statuses distinguish pass, failed expectation, and setup/usage error.
