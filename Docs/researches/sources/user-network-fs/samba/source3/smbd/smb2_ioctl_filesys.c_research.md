# sources/user-network-fs/samba/source3/smbd/smb2_ioctl_filesys.c

Purpose: handles filesystem FSCTLs for compression, zeroing sparse data, allocated range queries, duplicate extents/offloaded clone, and VFS fallback.

Important APIs and types: `smb2_ioctl_filesys()` dispatches controls. `fsctl_get_cmprn()` / `fsctl_set_cmprn()` handle compression. `fsctl_zero_data()` handles `FSCTL_SET_ZERO_DATA`. `fsctl_qar()` plus seek/fill helpers handles `FSCTL_QUERY_ALLOCATED_RANGES`. `fsctl_dup_extents_send()` / `fsctl_dup_extents_recv()` implement async duplicate extents through VFS offload.

Control flow: compression query returns VFS compression format or `COMPRESSION_FORMAT_NONE` when unsupported. Compression set requires write data, NDR-pulls state, and accepts setting `NONE` even without compression support. Zero-data requires write access, parses range, checks ordering and strict locks, punches a keep-size hole, and optionally reallocates under strict allocation for non-sparse files. QAR requires read data, validates range and output size, returns one range for non-sparse files or uses `SEEK_DATA`/`SEEK_HOLE` for sparse files, with `STATUS_BUFFER_OVERFLOW` for truncation. Duplicate extents requires block-refcounting support, NDR-pulls source fid/ranges, resolves same-volume source fsp, validates sizes, caps target length to EOF, rejects same-file overlap and sparse-source to non-sparse-target, obtains an offload token, and writes it to the destination.

State and persistence: compression, zero-data, and duplicate extents mutate backend file metadata/data through VFS. QAR is read-only but observes live file size/sparse state. Duplicate extents tracks async operation state.

Dependencies and integration: depends on generated IOCTL NDR, VFS compression/fallocate/lseek/offload hooks, strict lock checks, access checks, filesystem capability flags, `file_fsp_get()`, and common IOCTL response handling.

Risks: range arithmetic around EOF and overflow is critical. Hole punching must not extend files. QAR behavior changes when `HAVE_LSEEK_HOLE_DATA` is unavailable. Duplicate-extents target EOF capping is Windows-compatible but non-obvious. Same-file overlap and volume checks are correctness-sensitive.

Test signals: cover compression supported/unsupported, set `NONE` without support, zero-data zero/reversed ranges and lock conflict, QAR sparse/non-sparse and too-small output, duplicate extents invalid fid/cross-volume/overlap/zero length/target capping/short VFS write, and VFS fallback status mapping.
