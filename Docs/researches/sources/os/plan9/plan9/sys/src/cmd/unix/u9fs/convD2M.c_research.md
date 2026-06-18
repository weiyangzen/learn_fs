# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/convD2M.c

Serializes a Plan 9 `Dir` structure into 9P stat message format.

Functions:
- `sizeD2M` computes required bytes from fixed stat size plus four strings: name, uid, gid, muid.
- `convD2M` writes size, type, dev, qid, mode, times, length, and the four counted strings.

Notable behavior:
- If the buffer is too small, it writes the size field first and returns `BIT16SZ` so callers can learn the required size.
- Returns `0` on malformed/internal mismatch or bounds failure.
