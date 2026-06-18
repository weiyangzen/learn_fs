# sources/test-tools/liburing/.github/workflows/test_build.c

## sources/test-tools/liburing/.github/workflows/test_build.c

Purpose: Minimal installed-library smoke test used by CI to prove headers and linker artifacts from `make install` are usable by external C and C++ compilation commands.

Important APIs/functions: includes `<liburing.h>`, declares `struct io_uring`, calls `io_uring_queue_init(8, &ring, 0)`, then `io_uring_queue_exit(&ring)`.

Control flow: initialize ring, immediately tear it down, return zero. There is no error checking because the file is primarily a compile/link smoke test, not a runtime behavior test.

State and persistence: creates an io_uring instance at runtime if executed, but CI only needs successful compile/link into `a.out`.

Dependencies/integration: depends on installed liburing headers and `-luring`. CI compiles it once as C and once as C++ to catch header compatibility issues.

Risks: missing error handling means execution on kernels without io_uring could still return zero if the init failed, but the intended signal is build linkage. It does not test pkg-config or runtime library search paths.

Test signals: compiler and linker success in CI after install.
