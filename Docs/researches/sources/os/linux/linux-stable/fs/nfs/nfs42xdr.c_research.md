# File Research: sources/os/linux/linux-stable/fs/nfs/nfs42xdr.c

This file contains NFSv4.2 XDR size accounting, encoders, and decoders for v4.2 compound operations. It is included as the v4.2 XDR implementation and defines operation-specific maximum sizes and compound request/reply sizes.

Operations covered:
- `ALLOCATE`
- `COPY`
- `OFFLOAD_CANCEL`
- `OFFLOAD_STATUS`
- `COPY_NOTIFY`
- `DEALLOCATE`
- `ZERO_RANGE`
- `READ_PLUS`
- `SEEK`
- `LAYOUTSTATS`
- `LAYOUTERROR`
- `CLONE`
- `GETXATTR`
- `SETXATTR`
- `LISTXATTRS`
- `REMOVEXATTR`

Key size definitions:
- Per-operation encode/decode max sizes.
- Compound request/reply sizes such as `NFS4_enc_copy_sz`, `NFS4_dec_read_plus_sz`, and xattr-specific sizes.
- Exported overhead constants:
  - `nfs42_maxsetxattr_overhead`
  - `nfs42_maxgetxattr_overhead`
  - `nfs42_maxlistxattrs_overhead`
  These are used to constrain xattr sizes by session channel limits.

Encoder highlights:
- Encoders build compound sequences: compound header, `SEQUENCE`, `PUTFH`, operation, optional `SAVEFH`, optional `COMMIT`, optional `GETATTR`, then `encode_nops()`.
- `encode_copy()` supports intra-server copy and one source server for inter-server copy.
- `encode_zero_range()` composes `DEALLOCATE` then `ALLOCATE`.
- `encode_read_plus()` prepares reply pages with room for read-plus segment overhead.
- `encode_getxattr()` and `encode_listxattrs()` prepare reply pages for variable-sized xattr data.
- `encode_layoutstats()` allows layout-driver private encoding via `ld_private.ops`.

Decoder highlights:
- Basic operation decoders verify op headers and parse operation payloads.
- `decode_write_response()` handles optional callback stateid, byte count, committed level, and verifier.
- `decode_copy()` special-cases `NFS4ERR_OFFLOAD_NO_REQS` to decode server sync/consecutive requirements.
- `decode_offload_status()` decodes partial byte count and optional completion status.
- `decode_read_plus()` parses multiple sparse data/hole segments, then moves data or zero-fills target reply pages.
- `decode_listxattrs()` prefixes returned names with `user.`, enforces name length limits, handles `NFS4ERR_TOOSMALL` as `-ERANGE`, maps no-xattr to zero-length success, and turns max-size `-ERANGE` into `-E2BIG`.
- Mutating xattr decoders parse `change_info` and follow-up attributes.

Risk areas:
- `READ_PLUS` segment processing is delicate: it decodes segments first, then processes them backward while reshaping the XDR page buffer.
- Xattr page lengths and reply lengths are intentionally decoupled from caller buffer lengths to allow caching of oversized successful replies.
- LISTXATTRS sizing follows RFC 8276 count semantics and adds cookie/names-count overhead.
- Many decoders return protocol-level errors directly or translate selected protocol errors; this affects higher-level fallback behavior.
