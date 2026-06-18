# File Research: sources/virtualization/nbdkit/filters/blocksize/blocksize.c

Purpose: adapts arbitrary client request sizes to an underlying plugin’s stricter block-size requirements.

Key details:
- Configures `minblock`, `maxdata`, and `maxlen`.
- Validates `minblock` as a power of two no larger than 64 KiB; `maxdata`/`maxlen` must align to `minblock` when both are set.
- Per-connection handle values are finalized in `.prepare` by combining user configuration with backend block-size constraints.
- Advertises permissive client constraints: minimum `1`, maximum `0xffffffff`, and preferred at least `4096`/`minblock`.
- Uses a global `pthread_rwlock_t` and one shared bounce buffer for unaligned head/tail handling.
- `.pread` splits unaligned requests into aligned backend reads plus buffer copies.
- `.pwrite` and `.zero` use read-modify-write for unaligned heads/tails; aligned bodies use shared read locks.
- FUA is emulated by clearing `NBDKIT_FLAG_FUA` and flushing when the backend reports `NBDKIT_FUA_EMULATE`.
- `.trim` ignores unaligned edges and trims only aligned body regions.
- `.extents` asks backend for block-aligned extents and copies them to the caller.
- `.cache` rounds requested ranges outward to aligned backend cache calls.

Risk notes:
- Serialization is centered on one bounce buffer; correctness depends on using exclusive locking on every bounce-buffer path.
- Size is rounded down to `minblock`, so clients see a truncated virtual size when backend size is not aligned.
