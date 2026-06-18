# File Research: sources/virtualization/spdk/lib/env_ocf/ocf_env.c

Implements non-inline pieces of the OCF userspace environment on top of SPDK.

Important behavior:
- `env_allocator_*` wraps `spdk_mempool_create/get/put/free`.
- Allocator names are qualified with a global atomic index to keep names unique.
- Default allocator depth is `16383` objects unless a custom limit is supplied.
- Destroy checks that all objects were returned before freeing the mempool.
- `env_crc32()` delegates to `spdk_crc32_ieee_update()`.
- Execution-context emulation allocates one pthread mutex per online CPU at constructor time.
- `env_get_execution_context()` locks the current CPU's mutex based on `sched_getcpu()` and returns the CPU index; `env_put_execution_context()` unlocks it.

Compatibility role: supplies OCF with kernel-like allocator, CRC, and execution-context primitives in SPDK userspace.
