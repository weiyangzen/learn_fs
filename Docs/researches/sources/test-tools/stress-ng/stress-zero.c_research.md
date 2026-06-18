# sources/test-tools/stress-ng/stress-zero.c

Purpose: implements the `zero` stressor, exercising `/dev/zero` reads, optional writes, Linux mmap behavior, lseek, and ioctl paths while verifying that bytes read or mapped from the device are zero.

Important APIs/types/functions: `stress_zero`, `stress_zero_info`, `mmap_flags_t`, `mmap_flags`, `stress_mmap_populate`, `stress_madvise_mergeable`, `stress_data_is_not_zero`, `stress_munmap_force`, `open`, `read`, optional `write`, `mmap`, `munmap`, `lseek`, `ioctl`, `FIONBIO`, `FIONREAD`, `FIGETBSZ`, and option `zero-read`.

Control flow: the stressor maps page-sized read and write buffers, opens `/dev/zero` read/write except on Minix, synchronizes, and either runs a read-only benchmark loop or the broader exercise loop. Read-only mode continuously reads one page, counts bytes and bogo operations, and validates the final buffer. Full mode batches reads, verifies zero data, writes a page where supported, periodically mmaps `/dev/zero` with rotating anonymous/private/shared/locked/populate flag combinations on Linux and verifies mapped zeros, performs several lseek probes, toggles nonblocking ioctl state where available, probes read-size and block-size ioctls, and increments bogo operations. It closes the device, unmaps buffers, and publishes MB/sec read rate.

State and persistence behavior: state is limited to two anonymous page buffers, an open `/dev/zero` descriptor, byte counters, timing totals, and temporary Linux mappings. No persistent files are created and `/dev/zero` itself has no retained content.

Dependencies and integration points: uses stress-ng mmap, madvise, memory naming, metrics, option parsing, synchronization, and process-state helpers. Linux-specific mmap flag cycling is guarded by `__linux__`; Minix uses read-only open flags. The stressor registers as `CLASS_DEV | CLASS_MEMORY | CLASS_OS` with always-on verification.

Risks and test signals: failures include inability to open or read `/dev/zero`, non-zero data from reads or mappings, unexpected mmap failures other than transient memory pressure, and write/ioctl errors outside tolerated transient cases. Metrics can be skewed in full mode because mmap/ioctl/lseek work is interleaved with reads; `--zero-read` isolates read throughput.
