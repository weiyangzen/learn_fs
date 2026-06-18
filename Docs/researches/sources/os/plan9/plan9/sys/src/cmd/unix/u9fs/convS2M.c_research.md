# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/convS2M.c

Serializes an `Fcall` into 9P wire format.

Major helpers:
- `pstring` writes a counted string.
- `pqid` writes a serialized `Qid`.
- `stringsz` and `sizeS2M` compute serialized message size.

`convS2M` behavior:
- Computes exact size, rejects unknown message types and undersized buffers.
- Writes size, type, tag, and type-specific fields for T/R 9P messages.
- Handles counted strings, qids, walk arrays, read/write data, stat buffers, and auth qids.
- Enforces `MAXWELEM` for walk names/qids.
- Returns serialized size only if the write pointer matches the computed size.

Notable behavior:
- Contains commented-out older/session auth message variants.
