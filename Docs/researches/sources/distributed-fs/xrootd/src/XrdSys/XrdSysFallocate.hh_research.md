## sources/distributed-fs/xrootd/src/XrdSys/XrdSysFallocate.hh

Purpose: declares or includes platform support for `posix_fallocate`.

Important APIs/types/functions: on macOS, declares `extern int posix_fallocate(int fd, off_t offset, off_t len);`; elsewhere includes `<fcntl.h>` so the system declaration is available.

Control flow: compile-time branch only.

State and persistence: none in the header; the function mutates file allocation when called.

Dependencies and integration: used by code that needs file-space preallocation without carrying platform-specific includes. It relies on the `.cc` macOS shim being linked where required.

Risks: the header uses `off_t` in the macOS branch without including a type header locally, so include order matters. Return semantics must match caller expectations across platforms.

Test signals: compile on macOS and Linux with this header included first, link macOS shim, and verify caller handling of returned errors.
