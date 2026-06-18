# File Research: sources/virtualization/spdk/app/spdk_dd/spdk_dd.c

## Purpose
Implements `spdk_dd`, an asynchronous dd-like copy utility that copies between regular/block files and SPDK bdevs with configurable block size, queue depth, offsets, count, sparse handling, and file I/O backend selection.

## Main Entry Points
- `main()` parses SPDK/app arguments, validates input/output choices, starts the SPDK app, frees resources, and finalizes.
- `dd_run()` opens input/output targets, validates sizes/alignment, allocates DMA buffers, initializes file I/O pollers, starts progress reporting, and seeds the pipeline.
- `dd_target_seek()`, `dd_target_populate_buffer()`, `dd_target_read()`, and `dd_target_write()` form the copy pipeline.
- `dd_aio_poll()` and `dd_uring_poll()` reap file I/O completions.
- SPDK bdev callbacks `_dd_read_bdev_done()`, `_dd_write_bdev_done()`, `_dd_bdev_seek_data_done()`, and `_dd_bdev_seek_hole_done()` continue bdev operations.
- `dd_finish()` handles app shutdown by setting an interrupt flag.
- `dd_exit()` closes targets, unregisters pollers, and stops the app.

## Internal Mechanics
The utility models input and output as `dd_target` objects of type file or bdev. It maintains a fixed pool of `dd_io` objects sized by queue depth. Each object cycles through populate, read, write, and seek stages.

For normal copying, `dd_target_populate_buffer()` prepares a chunk and submits a read; read completion submits a write; write completion schedules the next chunk. If the final write is not aligned to the output block size, it first reads the destination block into the buffer so the partial update can be written as a full native block.

For sparse mode, file input uses `lseek(SEEK_DATA/SEEK_HOLE)`. Bdev input uses `spdk_bdev_seek_data()` and `spdk_bdev_seek_hole()` with a queue to serialize seek operations. Output files are finalized with `ftruncate()` when needed to preserve holes through the requested copy span.

File I/O uses io_uring when compiled and not forced to AIO, otherwise Linux libaio. io_uring registers files and fixed buffers; libaio submits `iocb`s and polls events through an SPDK poller. Bdev I/O uses SPDK bdev descriptors and I/O channels.

## Options
Supports `--if`, `--of`, `--ib`, `--ob`, `--iflag`, `--oflag`, `--skip`, `--seek`, `--bs`, `--qd`, `--count`, `--aio`, and `--sparse`.

## Dependencies
Depends on SPDK app, bdev, event, fd, util/string, optional VMD include, Linux libaio, and optional liburing.

## Filesystem/Block Relevance
This is a practical bridge between POSIX files/block devices and SPDK bdevs. It exercises read/write alignment, sparse extent discovery, bdev seek data/hole APIs, and async file I/O integration.

## Risks and Notes
- Requires exactly one input source and one output target.
- `--bs` must be at least both native block sizes and must align to input bdev block size.
- File targets are opened read/write; output files are created/truncated unless flags prevent it.
- Sparse behavior depends on target support for seek data/hole semantics.
- Progress accounting is global to the single copy job.
