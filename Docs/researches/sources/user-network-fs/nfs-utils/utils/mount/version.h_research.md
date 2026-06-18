<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/version.h -->
# sources/user-network-fs/nfs-utils/utils/mount/version.h

## Purpose

`version.h` provides inline helpers for converting Linux kernel release strings into integer version codes used by compatibility decisions in mount utilities.

## Important APIs, types, and functions

`MAKE_VERSION(p, q, r)` packs major, minor, and patch into the traditional `major*65536 + minor*256 + patch` format. `linux_version_code` calls `uname`, parses the leading numeric release components with `sscanf`, and returns a packed code or `UINT_MAX` on failure.

## Control flow

`linux_version_code` obtains `struct utsname`, initializes minor/patch defaults to zero, parses at least the major version, and returns the packed result. Failure paths deliberately return `UINT_MAX` so future or unparseable kernels do not trigger old compatibility branches.

## State and persistence behavior

The helper has no persistent state. It reads the current kernel release via `uname` each time it is called.

## Dependencies and integration points

It depends on `<sys/utsname.h>`, `<limits.h>`, and `<stdio.h>`. `stropts.c`, `utils.c`, and `nfssvc.c` use it for kernel feature decisions.

## Risks and edge cases

Distribution release suffixes are accepted if the numeric prefix parses, but unusual releases that do not start with an integer are treated as very new. Very large components can overflow the packed format. Repeated calls do not cache results.

## Test signals

Tests can wrap or simulate `uname` parsing for releases like `2.6.32`, `5.15.0-custom`, major-only strings, invalid strings, and very large numeric components.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/version.h -->
