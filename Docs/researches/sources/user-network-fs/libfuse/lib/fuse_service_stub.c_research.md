# sources/user-network-fs/libfuse/lib/fuse_service_stub.c

Purpose: `fuse_service_stub.c` provides ABI-compatible service-mount functions for builds or platforms where safe systemd container support is unavailable.

Important APIs, types, and functions: It defines the same exported service functions as `fuse_service.c`: file request/receive helpers, goodbye, accept, capability queries, arg append, command-line formatting/parsing, finish-file-requests, mount-format expectation, service session mount, release/destroy, and service exit.

Control flow: Most functions immediately return `-EOPNOTSUPP`, `false`, `NULL`, or `-1`. `fuse_service_accept` is deliberately non-fatal: it stores `NULL` in the output pointer and returns 0 to signal that no service socket was accepted. `fuse_service_destroy` nulls the caller's pointer. `fuse_service_exit` returns the input code unchanged.

State and persistence behavior: The stub owns no state and closes no resources. It never creates a `struct fuse_service` instance.

Dependencies and integration points: It includes `fuse_i.h` and `fuse_service.h` so callers can link against a consistent API regardless of `HAVE_SERVICEMOUNT`. `meson.build` chooses this file when service-mount support is disabled.

Risks: Callers must distinguish "not running as a service" from unsupported service operations. Code paths that unconditionally call request/mount helpers after a null accept will see `-EOPNOTSUPP`. Because release is a no-op, accidentally passing a real service pointer from a mismatched build would leak resources, though that should not occur with one selected implementation.

Test signals: Build/link tests with `HAVE_SERVICEMOUNT=false` should verify public symbols exist. Runtime tests should confirm `fuse_service_accept` returns success with no service and all service-only operations fail predictably.
