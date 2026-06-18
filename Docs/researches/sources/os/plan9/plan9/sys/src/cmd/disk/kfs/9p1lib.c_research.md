# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/9p1lib.c

This file implements 9P1 serialization/deserialization and old directory stat conversion.

Key behavior:
- `convS2M9p1` converts an `Oldfcall` into old 9P1 wire bytes.
- `convM2S9p1` parses wire bytes into `Oldfcall`, including in-buffer data pointers for read/write payloads.
- `convD2M9p1` converts a KFS `Dentry` into a fixed 116-byte old stat record.
- `convM2D9p1` parses the old stat record back into `Dentry`.
- `fakeqid9p1` mirrors the dump-fs qid workaround used in `9p1.c`.

Important details:
- Uses little-endian 16-bit and 32-bit field macros matching old Plan 9 wire format.
- Old stat records encode uid/gid as fixed `NAMELEN` strings and length as low/high 32-bit words, though KFS `Dentry.size` is a `long`.
- Mode conversion maps between old create/stat flags `PDIR`, `PAPND`, `PLOCK` and dentry flags `DDIR`, `DAPND`, `DLOCK`.

Dependencies:
- Requires `uidtostr` and `strtouid` from `uid.c`.
- Uses `Dentry`, `Qid9p1`, and mode constants from `portdat.h`/`dat.h`.
