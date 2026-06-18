# File Research: sources/os/linux/linux/fs/smb/client/compress.c

This file implements SMB 3.1.1 client-side send compression support when `CONFIG_CIFS_COMPRESSION` is enabled. It currently compresses write payloads with plain LZ77 and can request compressed reads when negotiated/share policy allow it.

Main pieces:
- Compressibility heuristic helpers derived from Btrfs compression logic.
- `should_compress()` decides whether a read/write SMB2 request should use compression.
- `smb_compress()` copies a write payload, LZ77-compresses it, wraps it in an SMB2 compression transform header, and invokes the supplied send function.

Compressibility heuristic:
- `collect_sample()` copies 2 KiB chunks with 2 KiB gaps from an `iov_iter`, capped at a 4 MiB sample window.
- `has_repeated_data()` accepts obvious repeated halves early.
- `is_mostly_ascii()` treats low distinct-byte-count ASCII-like data as compressible.
- `calc_byte_distribution()` classifies sorted byte-frequency buckets as bad/good/maybe.
- `has_low_entropy()` computes a Shannon-style integer entropy estimate and accepts only below threshold.
- Allocation/copy failures warn once and fail closed by returning not compressible.

Compression gating:
- Requires non-null `tcon`, session, server.
- Requires `server->compression.enabled`.
- Requires share flag `SMB2_SHAREFLAG_COMPRESS_DATA`.
- For writes, requires `Length >= SMB_COMPRESS_MIN_LEN` and `is_compressible(&rq->rq_iter)`.
- For reads, returns true if the command is `SMB2_READ` after negotiation/share checks.

`sm渲b_compress()` behavior:
- Validates the request is a single `smb2_write_req` header vector.
- Copies the original payload from `rq_iter` into a temporary source buffer without mutating the original iterator.
- Allocates destination size using `lz77_compressed_alloc_size()`.
- On successful and smaller LZ77 output, sends three vectors: compression transform header, original SMB2 write request header, compressed payload.
- If compression fails with `-EMSGSIZE` or output is not smaller, sends the original request uncompressed.
- Frees temporary buffers on all normal exits.

Dependencies:
- Uses SMB2 wire structures from `../common/smb2pdu.h`, CIFS globals/prototypes, and `compress/lz77.h`.
- The caller supplies `compress_send_fn`, keeping transport sending outside this file.
