# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsuid.h

Purpose: Defines Ghostscript font/object UID representation for PostScript `UniqueID` and Level 2 `XUID`.

Key definitions:
- `struct gs_uid_s` stores either a positive `UniqueID` in `id`, or an `XUID` encoded as negative length plus `xvalues`.
- `no_UniqueID` is `max_long`.
- Macros classify, initialize, invalidate, access, and free UIDs.

Declared functions:
- `uid_equal()` compares UIDs; implemented in `gsutil.c`.
- `uid_copy()` deep-copies XUID arrays when necessary; implemented in `gsutil.c`.

Behavior:
- Positive IDs represent simple `UniqueID`.
- Negative IDs represent XUID arrays of length `-id`.
- Invalid UID has `id == no_UniqueID` and `xvalues == 0`.

Dependencies:
- Requires `gs_memory_t`, `client_name_t`, and `max_long` definitions from broader Ghostscript headers.

Notable risks:
- `uid_free()` blindly frees `xvalues`; callers must only use it when ownership was established appropriately.
