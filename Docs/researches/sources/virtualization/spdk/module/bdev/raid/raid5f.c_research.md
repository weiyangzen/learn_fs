# File Research: sources/virtualization/spdk/module/bdev/raid/raid5f.c

## Purpose
Implements SPDK RAID level `SPDK_BDEV_RAID_LEVEL_RAID5F`, a full-stripe RAID5 bdev module. It supports full-stripe writes, direct reads from data chunks, degraded reads reconstructed from parity, and process/rebuild requests for missing base devices.

## Main Structures
- `struct chunk`: per-base-device chunk descriptor with chunk index, data iovecs, and metadata buffer.
- `struct stripe_request`: reusable per-channel work object for full-stripe writes or reconstruction reads. Tracks RAID I/O, stripe index, parity/reconstructed chunk, XOR state, buffers, and chunk array.
- `struct raid5f_info`: module-private RAID geometry: stripe blocks, total stripes, buffer alignment, block-length shift.
- `struct raid5f_io_channel`: channel-private pools of write/reconstruct stripe requests plus SPDK accel channel and XOR retry queue.

## Control Flow
`raid5f_start()` normalizes base bdev usable sizes to full strips, computes exported RAID block count, sets optimal/write-unit boundaries, stores module-private geometry, and registers an I/O device.

Writes are accepted only as full-stripe writes aligned to stripe boundaries. `raid5f_submit_write_request()` maps the user iovecs across data chunks, allocates/parses a parity chunk buffer, computes parity using `spdk_accel_submit_xor()`, then submits writes to all chunks. If the parity base device is missing, it skips parity XOR and treats the parity write as successfully omitted.

Reads normally map to a single data chunk. If the target chunk’s base channel is missing, `raid5f_submit_reconstruct_read()` reads the other data chunks plus parity and XORs them to reconstruct the missing data into the caller’s buffer.

`raid5f_submit_process_request()` supports rebuilding a missing target chunk. It reconstructs one strip using the same XOR path, then writes the reconstructed strip to the target base bdev.

## Dependencies
Depends on `bdev_raid.h`, SPDK bdev extension submission helpers, SPDK I/O channels, DMA allocation, iovec iterators, and the SPDK accel framework XOR operation. Metadata parity is handled when non-interleaved metadata is present.

## Invariants And Risks
- This is full-stripe RAID5: writes assert stripe alignment and full stripe length.
- `RAID5F_MAX_STRIPES` limits concurrent write and reconstruct stripe requests per channel to 32 each.
- XOR `-ENOMEM` is queued on a channel-local retry queue; other XOR errors fail the parent I/O.
- Reconstruction assumes at most one base device removed, enforced by module constraints.
- Metadata handling depends on non-interleaved metadata and `blocklen_shift`; interleaved metadata disables the shift path.
