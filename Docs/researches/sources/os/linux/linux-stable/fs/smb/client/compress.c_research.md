# File Research: sources/os/linux/linux-stable/fs/smb/client/compress.c

## Role

SMB 3.1.1 client-side I/O compression support for outgoing SMB2 write messages and compression eligibility checks for SMB2 read/write traffic. It implements the policy layer around negotiated compression, share flags, compressibility heuristics, LZ77 compression, compression transform header construction, and fallback to uncompressed sending.

## Key Functions

- `should_compress()` decides whether a request should use SMB compression.
  - Requires a valid tree/session/server.
  - Requires negotiated server compression and `SMB2_SHAREFLAG_COMPRESS_DATA`.
  - Allows reads when share/server compression is enabled.
  - Allows writes only when the write length is at least `SMB_COMPRESS_MIN_LEN` and `is_compressible()` accepts the request iterator.
- `smb_compress()` compresses an SMB2 write request before sending.
  - Validates the request shape as a single `smb2_write_req` iovec.
  - Copies the original write payload out of the iterator into a temporary source buffer.
  - Allocates a destination buffer using `lz77_compressed_alloc_size()`.
  - Calls `lz77_compress()`.
  - On success, wraps the original SMB2 write header and compressed payload in `struct smb2_compression_hdr` and sends a three-iovec request.
  - On `-EMSGSIZE` or non-smaller output, falls back to the original uncompressed request.

## Compressibility Heuristic

The heuristics are derived from Btrfs compression sampling logic and operate on a sampled copy of the write iterator:

- `collect_sample()` copies 2 KiB chunks with 2 KiB gaps, up to a 4 MiB sample.
- `has_repeated_data()` accepts exact repeated halves early.
- `is_mostly_ascii()` treats a narrow byte alphabet as likely compressible.
- `calc_byte_distribution()` sorts byte buckets by count and classifies distribution as good, bad, or maybe.
- `has_low_entropy()` computes an integer Shannon-entropy approximation and rejects data above the threshold.

The heuristic deliberately avoids compressing data that looks random, encrypted, or unlikely to benefit from LZ77.

## Dependencies and Integration

- Uses `struct smb_rqst`, `struct iov_iter`, and SMB2 headers from CIFS/SMB common headers.
- Uses `lz77_compress()` from `compress/lz77.c`.
- The send path is abstracted behind `compress_send_fn`, allowing the caller to provide the normal SMB send function.
- Uses `smb_EIO()` trace helpers for copy failure reporting and normal `kvzalloc()`/`kvfree()` lifetime for temporary buffers.

## Risk Notes

The compressor copies the full write payload before compression, so memory use scales with request size plus worst-case compressed allocation. The fallback behavior is conservative: failure to compress due to bad ratio sends the original request, while allocation and copy failures propagate errors.
