# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/vers.c

Defines the kernel `utsname` template.

Contents:
- Includes `sys/utsname.h`.
- Initializes global `struct utsname utsname` with `"SunOS"`, an empty nodename slot, and build-provided `UTS_RELEASE`, `UTS_VERSION`, and `UTS_PLATFORM`.

Filesystem relevance:
- No direct filesystem logic. The values can appear in system identity queries and diagnostics that accompany filesystem and kernel reports.
