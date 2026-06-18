# File Research: sources/os/bsd/dragonflybsd/sys/sys/ucred.h

## Summary
Kernel credential structure and external credential representation.

## Main Responsibilities
- Defines `struct ucred` with effective/real/saved IDs, groups, uid resource pointers, prison pointer, and system capability restrictions.
- Places `cr_ref` in its own cache-aligned subobject to reduce cacheline ping-pong.
- Defines `NOCRED`, `FSCRED`, and `cr_gid`.
- Defines stable external `struct xucred` and `XUCRED_VERSION`.
- Declares kernel credential allocation, duplication, reference, conversion, and group-membership helpers.

## Important Behavior
The comment explicitly warns against inspecting `cr_uid` directly for superuser checks; privilege decisions should use `priv(9)`.

## Risks
Credential lifetime is reference-counted and shared. Incorrect direct mutation or privilege checks can produce security bugs, and `xucred` layout is externally visible.
