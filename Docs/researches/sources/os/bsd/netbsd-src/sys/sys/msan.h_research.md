# File Research: sources/os/bsd/netbsd-src/sys/sys/msan.h

## Purpose
Declares NetBSD KMSAN kernel memory sanitizer hooks and no-op stubs when KMSAN is disabled.

## Main API
- KMSAN states: `KMSAN_STATE_UNINIT`, `KMSAN_STATE_INITED`.
- Allocation/source types: `KMSAN_TYPE_STACK`, `KMSAN_TYPE_KMEM`, `KMSAN_TYPE_MALLOC`, `KMSAN_TYPE_POOL`, `KMSAN_TYPE_UVM`.
- DMA object types: `KMSAN_DMA_LINEAR`, `KMSAN_DMA_MBUF`, `KMSAN_DMA_UIO`, `KMSAN_DMA_RAW`.
- Runtime functions when enabled: `kmsan_init`, `kmsan_shadow_map`, `kmsan_lwp_alloc`, `kmsan_lwp_free`, `kmsan_dma_sync`, `kmsan_dma_load`, `kmsan_orig`, `kmsan_mark`, `kmsan_check_mbuf`, `kmsan_check_buf`.

## Dependencies
Includes `opt_kmsan.h` under `_KERNEL_OPT`; when `KMSAN` is enabled, depends on `sys/types.h` and `sys/bus.h`.

## Risks and Notes
When `KMSAN` is not defined, all hooks compile to `__nothing`. Code using these calls must not rely on side effects unless the sanitizer option is enabled.
