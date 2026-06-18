# sources/user-network-fs/nfs-utils/support/include/version.h

## Purpose
Provides inline Linux kernel version-code calculation for compatibility decisions.

## Important APIs, Types, and Functions
`MAKE_VERSION(p,q,r)` and `linux_version_code()`.

## Control Flow
`linux_version_code()` calls `uname()`, parses leading release numbers with `sscanf`, and returns a packed version or `UINT_MAX` on failure/unparseable future formats.

## State and Persistence Behavior
No persistent state. It reads current kernel release at call time.

## Dependencies and Integration Points
Used by mount/support code that gates behavior on kernel version.

## Risks and Edge Cases
`UINT_MAX` intentionally disables backward-compat paths, but unparseable releases may hide needed workarounds. Vendor suffixes after numbers are tolerated.

## Test Signals
Test parse of common releases, partial `major.minor`, uname failure injection, and future nonnumeric strings.
