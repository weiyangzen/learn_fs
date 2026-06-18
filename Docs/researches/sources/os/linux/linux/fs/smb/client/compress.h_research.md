# File Research: sources/os/linux/linux/fs/smb/client/compress.h

This header defines the public compression interface for the CIFS/SMB client.

Key definitions:
- `SMB_COMPRESS_HDR_LEN` is 16, excluding `OriginalPayloadSize`.
- `SMB_COMPRESS_PAYLOAD_HDR_LEN` is 8, excluding `OriginalPayloadSize`.
- `SMB_COMPRESS_MIN_LEN` is `PAGE_SIZE`.
- `compress_send_fn` is the callback type used by `smb_compress()` to send either transformed or original requests.

When `CONFIG_CIFS_COMPRESSION` is enabled:
- Exposes `smb_compress()`.
- Exposes `should_compress()`.
- Provides `smb_compress_alg_valid()`, accepting `SMB3_COMPRESS_LZ77` and `SMB3_COMPRESS_PATTERN`; `SMB3_COMPRESS_NONE` is conditionally valid based on the caller’s `valid_none` argument.

When compression is disabled:
- `smb_compress()` returns `-EOPNOTSUPP`.
- `should_compress()` returns false.
- `smb_compress_alg_valid()` returns `-EOPNOTSUPP`.

Important semantic note:
- The header documents that `SMB3_COMPRESS_NONE` is not valid during protocol negotiation, even though some callers may allow it in non-negotiation contexts.
