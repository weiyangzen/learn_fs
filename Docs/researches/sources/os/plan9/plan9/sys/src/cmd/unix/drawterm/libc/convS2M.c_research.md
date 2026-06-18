# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/convS2M.c

This file encodes `Fcall` structures into 9P protocol messages.

Key behavior:
- `sizeS2M` computes encoded message size by 9P type.
- `convS2M` writes size/type/tag and all type-specific fields, qids, strings, data payloads, and stat payloads.
- `pstring` and `pqid` encode counted strings and qids.

Important details:
- Rejects unknown message types, oversized walk/qid arrays, and caller buffers smaller than computed size.
- Contains an apparent duplicated `PBIT32(p, f->fid);` in `Topen`; the final size check can detect pointer mismatch if it changes encoded length.
