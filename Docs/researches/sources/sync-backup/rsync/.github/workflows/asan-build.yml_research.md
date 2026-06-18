# sources/sync-backup/rsync/.github/workflows/asan-build.yml

Purpose: sanitizer CI for memory safety and undefined behavior.

Important APIs/types/functions: weekly/push/PR/workflow_dispatch triggers. Uses clang with `-fsanitize=address,undefined`, `-fno-sanitize-recover=undefined`, `-DNDEBUG`, ASAN leak detection disabled, UBSan fatal.

Control flow: installs deps, configures `--with-rrsync --disable-md2man`, builds `check-progs`, prints version, runs default and TCP daemon test suites.

State and persistence: no artifacts on success; sanitizer failures surface in logs.

Dependencies/integration: depends on clang, ASan/UBSan runtimes, ACL/xattr/compression/OpenSSL development packages.

Risks: sanitizer/toolchain changes can create new findings; deliberate byteorder unaligned accesses need suppression/attributes in source.

Test signals: `runtests.py` under instrumented binary over both transports.
