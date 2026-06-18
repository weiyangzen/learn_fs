<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/version.c -->
## sources/test-tools/liburing/src/version.c

Purpose: implements runtime liburing version checks.

Important APIs/types/functions: `io_uring_major_version` returns `IO_URING_VERSION_MAJOR`; `io_uring_minor_version` returns `IO_URING_VERSION_MINOR`; `io_uring_check_version` returns true when the runtime library is at least the requested major/minor pair.

Control flow: `io_uring_check_version` first compares major, then minor when majors match.

State and persistence behavior: no mutable state. Values come from generated `io_uring_version.h`.

Dependencies and integration points: included through `liburing.h` declarations and version macros. Applications can use both runtime and compile-time version checks.

Risks: the compile-time macro `IO_URING_CHECK_VERSION` in the header appears to express "requested version is newer than current" semantics, while the runtime function expresses "current is at least requested"; callers must choose the right one.

Test signals: simple ABI/version tests would catch symbol availability. Most functional tests do not depend on this file.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/version.c -->
