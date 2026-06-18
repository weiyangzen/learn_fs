# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/error.c

Shared gefs error-string definitions.

Key contents:
- Defines internal errors for corruption, implementation gaps, protocol botches, I/O, fids, types, search, permissions, auth, snapshots, readonly state, and qid exhaustion.
- Defines Plan 9 wstat-specific errors for illegal qid/mode/name/owner/group/length changes.
- Keeps old/commented error strings as historical references.

Role:
- Provides stable `char[]` error symbols used with `error()`, `broke()`, and 9P `Rerror` responses.
