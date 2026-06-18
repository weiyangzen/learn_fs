# File Research: sources/virtualization/spdk/lib/env_ocf/ocf_env.h

Defines the main OCF environment compatibility API for SPDK.

Important contents:
- Provides Linux-style scalar aliases, packed/aligned attributes, sector constants, `container_of`, `ARRAY_SIZE`, `min`, and logging/bug macros.
- Maps OCF allocation APIs to SPDK DMA-capable `spdk_malloc`, `spdk_zmalloc`, and `spdk_free`.
- Declares `env_allocator` and allocator functions implemented in `ocf_env.c`.
- Implements mutexes, recursive mutexes, rw semaphores, spinlocks, rwlocks, completions, waitqueues, atomics, and bit operations with pthreads, semaphores, and GCC sync builtins.
- Provides tick/time conversion wrappers over `spdk_get_ticks()` and `spdk_get_ticks_hz()`.
- Implements bounded memory/string helpers with OCF-style success/failure return conventions.
- Declares CRC and execution-context functions implemented externally.

Filesystem/storage relevance: this header is the main contract that allows OCF cache logic to compile and run inside SPDK's userspace environment.
