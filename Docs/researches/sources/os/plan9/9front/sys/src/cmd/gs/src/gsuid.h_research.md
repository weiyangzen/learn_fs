# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsuid.h

Declares Ghostscript font/object unique identifier representation and helper macros.

Key definitions:
- `gs_uid` stores either a positive 24-bit-style `UniqueID` or a negative-size XUID vector.
- `no_UniqueID` uses `max_long` to represent absence of an identifier.
- Macros test validity, UniqueID/XUID form, initialize UniqueID or XUID values, and expose XUID size/data.
- Declares `uid_equal` and `uid_copy`, implemented in `gsutil.c`.
- `uid_free` frees the XUID array when present.

Research notes:
- A valid UniqueID is constrained by `uid_is_UniqueID` to values whose high bits outside `0xffffff` are clear.
- XUID storage ownership is external until `uid_copy` duplicates it.
