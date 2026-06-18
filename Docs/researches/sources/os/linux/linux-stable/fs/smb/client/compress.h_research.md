# File Research: sources/os/linux/linux-stable/fs/smb/client/compress.h

## Role

Public CIFS client header for SMB 3.1.1 compression support. It defines compression header sizing constants, minimum compression size, the compressed-send callback type, compression entry points, algorithm validation, and disabled stubs for builds without `CONFIG_CIFS_COMPRESSION`.

## Key Definitions

- `SMB_COMPRESS_HDR_LEN` is the SMB2 compression transform header length excluding `OriginalPayloadSize`.
- `SMB_COMPRESS_PAYLOAD_HDR_LEN` is the chained payload header length excluding `OriginalPayloadSize`.
- `SMB_COMPRESS_MIN_LEN` is `PAGE_SIZE`; writes smaller than this are not considered for compression.
- `compress_send_fn` is the callback signature used by `smb_compress()` to send either compressed or fallback requests.

## API Surface

- `smb_compress(struct TCP_Server_Info *server, struct smb_rqst *rq, compress_send_fn send_fn)` compresses and sends an SMB request when supported.
- `should_compress(const struct cifs_tcon *tcon, const struct smb_rqst *rq)` evaluates negotiated capability, share flags, command type, size, and data compressibility.
- `smb_compress_alg_valid(__le16 alg, bool valid_none)` accepts `SMB3_COMPRESS_LZ77` and `SMB3_COMPRESS_PATTERN`, and accepts `SMB3_COMPRESS_NONE` only when the caller explicitly allows it.

## Build-Time Behavior

When `CONFIG_CIFS_COMPRESSION` is disabled, the header provides inline stubs:

- `smb_compress()` returns `-EOPNOTSUPP`.
- `should_compress()` returns `false`.
- `smb_compress_alg_valid()` returns `-EOPNOTSUPP`.

## Research Notes

The header is intentionally narrow. It exposes only the policy/send entry points and validation helper; algorithm internals live under `compress/`.
