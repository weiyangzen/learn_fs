# sources/test-tools/stress-ng/stress-seal.c

Purpose: implements `seal`, a Linux memfd sealing stressor that creates sealable anonymous files and verifies that shrink, grow, write, execute, and future-write seals enforce expected permissions.

Important APIs/types/functions: `stress_seal_info` is `CLASS_OS`, `VERIFY_ALWAYS`. `stress_seal()` uses `shim_memfd_create()`, `ftruncate()`, `fcntl(F_GET_SEALS/F_ADD_SEALS)`, shared writable `mmap()`, `write()`, `fchmod()`, and optional `F_SEAL_EXEC`/`F_SEAL_FUTURE_WRITE`. Fallback defines cover seal constants and `MFD_ALLOW_SEALING`.

Control flow: the stressor allocates one page of write buffer, synchronizes, and loops. Each iteration creates a memfd with a randomized name, truncates to one page, confirms seal retrieval, adds `F_SEAL_SHRINK` and verifies shrink fails with EPERM, adds `F_SEAL_GROW` and verifies growth fails, maps the file writable and verifies `F_SEAL_WRITE` fails with EBUSY while mapped, unmaps, adds `F_SEAL_WRITE`, verifies writes fail, optionally adds exec/future-write seals and checks chmod/mmap behavior, then closes and increments bogo.

State and persistence: state is one anonymous buffer and per-iteration memfd file descriptors. Memfds are anonymous kernel objects and disappear on close. Cleanup unmaps the buffer and closes current fd paths.

Dependencies and integration points: requires Linux and `memfd_create()`. It uses stress-ng mmap, madvise, memory naming, sync, random naming, and diagnostics.

Risks and test signals: kernel support for newer seals varies, and writable mappings can legitimately cause EBUSY. Test signals are expected EPERM/EBUSY failures, successful bogo increments per complete memfd seal cycle, and no fd/mapping leaks.
