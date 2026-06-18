# File Research: sources/os/linux/linux/fs/nfs/nfs42xdr.c

This file contains NFSv4.2 XDR size accounting, encoders, and decoders for v4.2 compound operations. It is guarded as an include-style implementation header and defines operation-specific maximum sizes plus compound request/reply sizes.

Operations covered:
- `ALLOCATE`, `DEALLOCATE`, and `ZERO_RANGE`.
- `COPY`, `COPY_NOTIFY`, `OFFLOAD_CANCEL`, and `OFFLOAD_STATUS`.
- `READ_PLUS` and `SEEK`.
- pNFS `LAYOUTSTATS` and `LAYOUTERROR`.
- `CLONE`.
- `GETXATTR`, `SETXATTR`, `LISTXATTRS`, and `REMOVEXATTR`.

Key size definitions:
- Per-operation encode/decode limits such as `encode_copy_maxsz`, `decode_read_plus_maxsz`, and xattr encode/decode sizes.
- Compound totals such as `NFS4_enc_copy_sz`, `NFS4_dec_read_plus_sz`, and xattr-specific totals.
- Exported overhead constants `nfs42_maxsetxattr_overhead`, `nfs42_maxgetxattr_overhead`, and `nfs42_maxlistxattrs_overhead`, used by session setup to clamp xattr transfer sizes.

Encoder behavior:
- Encoders build standard compounds with header, `SEQUENCE`, `PUTFH`, operation-specific bodies, and optional `SAVEFH`, `COMMIT`, or `GETATTR`.
- `encode_copy()` supports intra-server copy and a single source server for inter-server copy.
- `encode_zero_range()` composes `DEALLOCATE` followed by `ALLOCATE`.
- `encode_read_plus()` prepares sparse read requests using stateid, offset, and count.
- `encode_layoutstats()` delegates layout-driver private encoding when `ld_private.ops` is present.
- Xattr encoders write names and page-backed values, with `LISTXATTRS` count following RFC 8276 reply-size semantics.

Decoder behavior:
- Basic decoders verify operation headers and then parse operation-specific payloads.
- `decode_write_response()` parses optional callback stateid, byte count, committed level, and verifier.
- `decode_copy()` special-cases `NFS4ERR_OFFLOAD_NO_REQS` to decode server sync/consecutive requirements.
- `decode_offload_status()` decodes copied byte count and optional completion status array.
- `decode_read_plus()` parses sparse data/hole segments, then processes them backwards to move data or zero-fill target reply pages.
- `decode_listxattrs()` prefixes returned names with `user.`, enforces name limits, maps `NFS4ERR_TOOSMALL` to `-ERANGE`, maps no-xattr to zero-length success, and turns max-size `-ERANGE` into `-E2BIG`.
- Mutating xattr decoders parse `change_info` and follow-up attributes.

Dependencies:
- Requires shared NFSv4 XDR helpers for compound headers, sequence, filehandle, stateid, verifier, commit, attributes, opaque strings, and XDR page manipulation.
- Uses constants from `nfs42.h`, NFSv4 protocol headers, xattr UAPI limits, and pNFS layout stats limits.

Risk areas:
- `READ_PLUS` buffer rewriting is delicate because segments are first decoded and then moved/zeroed into the receive page buffer.
- Xattr reply page length is intentionally separate from caller buffer length so successful oversized replies can still be cached.
- LISTXATTRS name sizing combines server count semantics with Linux `user.` prefixing and NUL terminators.
- Decoder status translation feeds directly into higher-level retry and fallback behavior.
