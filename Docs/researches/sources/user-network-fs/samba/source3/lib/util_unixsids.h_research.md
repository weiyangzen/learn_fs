# sources/user-network-fs/samba/source3/lib/util_unixsids.h

## Purpose
This header declares the Unix Users and Unix Groups synthetic SID helper interface.

## Important APIs and Types
It forward-declares `struct dom_sid` and exposes checks, uid/gid SID composition, and display domain-name helpers.

## Dependencies and Integration Points
It includes `replace.h` for portability and is paired with `util_unixsids.c`. Callers are expected to include full SID definitions where they manipulate `struct dom_sid` storage.

## Risks and Test Signals
The header is low-risk but part of identity mapping ABI. Compile tests should cover consumers that include it before broader security headers.
