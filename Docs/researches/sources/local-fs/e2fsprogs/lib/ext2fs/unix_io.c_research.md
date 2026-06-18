# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/unix_io.c

## Purpose
POSIX/Unix implementation of the libext2fs I/O manager, including raw file/device I/O, a small write-back block cache, optional direct-I/O bounce buffering, stats, locking, discard, zeroout, and file-descriptor-backed channels.

## Main Behavior
- `raw_read_blk()` and `raw_write_blk()` perform positioned reads/writes using `pread/pwrite` when possible, falling back to `llseek` plus `read/write`.
- Unaligned direct I/O uses a bounce buffer and read-modify-write logic.
- The cache stores block-sized buffers, tracks dirty state and access time, flushes dirty entries on eviction/close/blocksize changes, and supports runtime resizing through `cache_blocks`.
- Large or odd-sized reads/writes bypass the cache after flushing.
- `unix_open_channel()` initializes channel metadata, detects block devices, direct-I/O alignment, discard-zeroes behavior, optional thread mutexes, and Linux read-only block-device status.

## Options / Operations
- `offset`: shifts all I/O by a byte offset.
- `cache=on|off`: toggles cache use.
- `cache_blocks`: grows or shrinks the block cache.
- `discard`: uses `BLKDISCARD` for block devices or `fallocate(PUNCH_HOLE)` for files.
- `zeroout`: uses `fallocate(ZERO_RANGE)` or hole punching for files, with regular-file extension when needed.
- `flock`: maps libext2fs flock flags to Unix `flock`.

## Integration
Exports `unix_io_manager` for path-based opening and `unixfd_io_manager` for existing file descriptors. Also supplies portable wrappers `ext2fs_open_file`, `ext2fs_stat`, and `ext2fs_fstat`.

## Risks / Notes
- Error handlers can be called during raw I/O and deferred cache flush failures.
- Direct-I/O alignment and bounce-buffer paths are central to correctness on block devices.
- `CHANNEL_FLAGS_NODISCARD` and `CHANNEL_FLAGS_NOZEROOUT` cache unsupported operations after `EOPNOTSUPP`.
