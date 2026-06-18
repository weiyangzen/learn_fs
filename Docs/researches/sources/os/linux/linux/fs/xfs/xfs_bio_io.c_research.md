# File Research: sources/os/linux/linux/fs/xfs/xfs_bio_io.c

Provides a small block-device read/write helper for XFS metadata buffers that may be virtually contiguous vmalloc memory.

Key elements:
- `bio_max_vecs` computes a segment count from a byte count.
- `xfs_rw_bdev` applies `REQ_META | REQ_SYNC`, uses `bdev_rw_virt` for non-vmalloc buffers, and builds/chains bios with `bio_add_vmalloc_chunk` for vmalloc buffers.
- On vmalloc input, allocates additional chained bios when the current bio cannot accept more chunks.
- Uses `submit_bio_wait` on the final bio and releases it.

Dependencies:
- Uses block layer bio helpers and `bdev_rw_virt`.
- Intended for synchronous metadata-oriented I/O.

Research notes:
- The code attempts to invalidate vmalloc mappings after reads, but compares `op == REQ_OP_READ` after OR-ing request flags into `op`; as written, that condition is unlikely to be true for read operations with flags attached.
- Bio chaining means only the final bio is waited on directly; earlier bios are chained to it.
