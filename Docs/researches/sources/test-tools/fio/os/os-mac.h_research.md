# sources/test-tools/fio/os/os-mac.h

## Purpose
`os-mac.h` adapts fio to macOS. It declares macOS feature support and implements direct-I/O toggling, disk/char device sizing, memory detection, thread id, native preallocation, CPU feature detection, byte swaps, and POSIX fadvise compatibility exposure.

## Important APIs, Types, and Functions
It defines `FIO_OS os_mac`, `FIO_USE_GENERIC_INIT_RANDOM_STATE`, `FIO_HAVE_GETTID`, `FIO_HAVE_CHARDEV_SIZE`, `FIO_HAVE_NATIVE_FALLOCATE`, `FIO_HAVE_CPU_HAS`, `FIO_OS_DIRECTIO`, and `CONFIG_POSIX_FADVISE`. Helpers include `fio_set_odirect()`, `blockdev_size()`, `chardev_size()`, `blockdev_invalidate_cache()`, `os_phys_mem()`, `gettid()`, `fio_fallocate()`, and `os_cpu_has()`.

## Control Flow
Direct I/O is approximated with `fcntl(F_NOCACHE)`. Block size uses `DKIOCGETBLOCKCOUNT` and `DKIOCGETBLOCKSIZE`; char-device size falls back to block sizing or reports unknown size. Preallocation calls `fcntl(F_PREALLOCATE)` followed by `ftruncate()`. CPU feature detection currently treats AArch64 macOS as supporting the CRC32C feature.

## State and Persistence
No global state is stored. Calls may alter fd cache behavior and preallocate/truncate files.

## Dependencies and Integration Points
It depends on macOS disk, sysctl, Mach thread, endian, and `OSByteOrder` APIs, plus `mac/posix.h`. Its macros enable common fio paths for native fallocate, fadvise, direct I/O setup, and CPU-accelerated checksums.

## Risks and Edge Cases
`mach_thread_self()` returns a send right that typical code should deallocate; using it as a thread id can be platform-specific. `fio_fallocate()` truncates to `len`, not `offset + len`, matching the local implementation but worth checking for nonzero offsets. `F_NOCACHE` is not identical to Linux `O_DIRECT`.

## Test Signals
macOS build tests, direct-I/O/fadvise jobs, raw disk size checks, native preallocation tests with nonzero offset, and ARM64 checksum feature selection tests are relevant.
