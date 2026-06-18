# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_msan.c

## Purpose
Implements the machine-independent part of NetBSD KMSAN, the kernel memory sanitizer runtime used by compiler instrumentation to track uninitialized-memory shadow/origin metadata. It supplies compiler ABI entry points, kernel wrapper hooks for memory/string/user-copy/atomic/bus/DMA operations, and report formatting for detected uninitialized reads.

## Main Entry Points
- `kmsan_init()`, `kmsan_shadow_map()`, `kmsan_lwp_alloc()`, `kmsan_lwp_free()`, `kmsan_intr_enter()`, `kmsan_intr_leave()`, and `kmsan_softint()` initialize global KMSAN state, per-LWP TLS contexts, interrupt nesting contexts, and shadow/origin mappings.
- `kmsan_mark()`, `kmsan_orig()`, `kmsan_check_mbuf()`, and `kmsan_check_buf()` expose kernel-facing marking/checking helpers.
- Compiler ABI functions include `__msan_metadata_ptr_for_load_n`, `__msan_metadata_ptr_for_store_n`, fixed-size metadata variants, `__msan_get_context_state()`, `__msan_poison_alloca()`, `__msan_unpoison_alloca()`, `__msan_instrument_asm_store()`, `__msan_chain_origin()`, and `__msan_warning()`.
- Wrapper functions include `kmsan_memcpy`, `kmsan_memset`, `kmsan_memmove`, `kmsan_memcmp`, string routines, `kmsan_kcopy`, `kmsan_copyin`, `kmsan_copyout`, `kmsan_copyinstr`, `kmsan_copyoutstr`, user fetch/store/CAS wrappers, generated atomic wrappers, bus-space read/write wrappers, and DMA sync/load helpers.

## Control Flow And State
The core helpers translate kernel addresses to shadow and origin metadata through MD hooks from `<machine/msan.h>`. Unsupported or disabled regions use dummy shadow/origin pages so compiler instrumentation can continue without touching invalid metadata. Shadow bytes mark initialized/uninitialized state; origin words encode stack/kmem/malloc/pool/uvm origin type plus either a program counter or stack descriptor.

Reports are guarded by `kmsan_reporting`, `panicstr`, and DDB activity to avoid recursion. Reporting decodes origins, optionally resolves symbols under a pserialize read section, prints via `kprintf` or `panic` depending on `KMSAN_PANIC`, unwinds with `kmsan_md_unwind()`, and releases the reporting guard.

Per-LWP sanitizer state is `msan_lwp_t`, holding a small stack of TLS contexts for normal and interrupt execution. `kmsan_enabled` gates all runtime work. `msan_lwp0` seeds the bootstrap LWP.

## Integration Points
Depends on machine-dependent KMSAN address/origin routines, kernel symbol lookup, pserialize, kprintf, copyin/copyout, atomics, bus space APIs, mbufs, bufs, uio, and bus DMA maps. `subr_pool.c` calls into KMSAN to poison/unpoison pool allocations.

## Risks And Notes
Correctness depends on exact compiler ABI names and on keeping wrappers semantically identical to the real kernel routines. Missing a wrapper can create false positives or false negatives. Origin handling assumes MD metadata mappings are valid for supported addresses. DMA and bus-space hooks intentionally mark post-read data initialized and check pre-write data, so wrong `dm_buftype` or sync flags can hide real bugs.
