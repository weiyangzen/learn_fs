# sources/user-network-fs/pyfuse3/src/pyfuse3/pyfuse3.h

Purpose: Central native header for platform detection, semaphore inclusion, and libfuse version gating.

Important APIs/types/functions: Defines `PLATFORM_LINUX`, `PLATFORM_BSD`, `PLATFORM_DARWIN`, sets `PLATFORM` based on compiler OS macros, includes `darwin_compat.h` on Darwin and `<semaphore.h>` elsewhere, includes `<fuse.h>`, and enforces `FUSE_VERSION >= 32`.

Control flow: Compilation fails early for unknown operating systems or libfuse versions older than 3.2.0.

State and persistence: No state; establishes compile-time constants and includes.

Dependencies and integration points: Used by native extension sources and paired with `util/build_backend.py`, which defines `FUSE_USE_VERSION=32` and links against `fuse3`.

Risks: Platform macro checks are strict; unsupported POSIX-like systems fail to build. The `__FreeBSD_kernel__ && __GLIBC__` branch assumes both macros can be tested safely.

Test signals: Any successful extension build validates this header for the host OS. CI matrix and package builds are the main coverage.
