# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_asan.c

Read completely: 1306 lines.

Implements NetBSD's kernel AddressSanitizer support glue. It provides shadow-memory mapping and poisoning helpers, access checking and reports, wrappers around memory/string/copy/atomic/bus/DMA operations, global registration handling, and compiler ASan ABI entry points.

Initialization and shadow mapping:
- `kasan_shadow_map()` maps shadow pages for a kernel address range after translating through machine-dependent `kasan_md_addr_to_shad()`.
- `kasan_early_init()` delegates early setup to `kasan_md_early_init()`.
- `kasan_init()` runs machine-dependent initialization, flips `kasan_enabled`, and calls compiler-generated ASan constructors from `__CTOR_LIST__` to `__CTOR_END__`.
- `kasan_softint()` marks an LWP uarea/stack region valid when used for soft interrupt context.
- The file includes `<machine/asan.h>` for MD constants and helpers, and enforces supported compiler ASan ABI versions.

Poisoning and validation:
- `kasan_add_redzone()` rounds allocation sizes to the shadow scale and appends one shadow-scale redzone.
- `kasan_mark()` marks the valid prefix of an allocation and poisons the redzone suffix with a caller-provided code.
- `kasan_shadow_Nbyte_fill()` fills shadow bytes with a poison code after alignment and unsupported-address checks.
- `kasan_shadow_1byte_markvalid()` and `kasan_shadow_Nbyte_markvalid()` make byte ranges addressable, including partial shadow-byte handling.
- Fast validators exist for 1, 2, 4, and 8-byte accesses, falling back to byte-by-byte validation for other sizes or boundary-crossing accesses.
- `kasan_shadow_check()` gates checks on `kasan_enabled`, DDB recovery state, zero size, and unsupported MD ranges, then calls `kasan_report()` on invalid access.

Reporting:
- `kasan_code_name()` maps poison codes to labels such as generic redzone, malloc/kmem/pool redzone, pool use-after-free, stack left/middle/right, use-after-return, and use-after-scope.
- `kasan_report()` prints or panics depending on `KASAN_PANIC`, includes access address, program counter, byte size, read/write direction, and poison label, then invokes `kasan_md_unwind()`.

Wrapped memory and user-copy APIs:
- `kasan_memcpy()`, `kasan_memmove()`, `kasan_memcmp()`, `kasan_memset()`, `kasan_strcpy()`, `kasan_strcmp()`, `kasan_strlen()`, `kasan_strcat()`, `kasan_strchr()`, and `kasan_strrchr()` check source and/or destination ranges before delegating to builtins.
- `kasan_kcopy()`, `kasan_copyin()`, `kasan_copyinstr()`, and `kasan_copyoutstr()` check only kernel buffers where appropriate before calling the underlying kernel copy routines.
- `_ucas_*` and `_ufetch_*` wrappers check kernel result/output buffers before invoking machine/user access primitives.

Atomic, bus, and DMA instrumentation:
- Macro families generate wrappers for add, and, or, compare-and-swap, swap, decrement, and increment atomic operations across 32-bit, 64-bit, int, long, uint, ulong, and pointer forms.
- Atomic wrappers validate the target memory as writable for the operation size before calling the original atomic primitive.
- When `__HAVE_KASAN_INSTR_BUS` is defined, macro families wrap bus-space read/write multi/region and stream variants for 1, 2, 4, and 8-byte element sizes.
- `kasan_dma_load()` records the buffer pointer, length, and buffer type in a DMA map.
- `kasan_dma_sync()` validates DMA buffers for linear buffers, mbuf chains, or kernel-space uios, using the sync operation flags to decide read/write direction; raw buffers are skipped.

Compiler ASan ABI:
- `__asan_register_globals()` poisons global-variable redzones according to compiler-provided descriptors.
- `__asan_unregister_globals()` is present but intentionally does nothing.
- `__asan_load{1,2,4,8,16}` and `__asan_store{1,2,4,8,16}` plus `_noabort` variants call `kasan_shadow_check()`.
- `__asan_loadN` and `__asan_storeN` handle dynamic sizes.
- `__asan_set_shadow_*` routines fill shadow memory with specific poison bytes.
- `__asan_poison_stack_memory()`, `__asan_unpoison_stack_memory()`, `__asan_alloca_poison()`, and `__asan_allocas_unpoison()` implement stack and alloca redzone ABI hooks.
- `__asan_handle_no_return()` is a no-op in this kernel implementation.

Risks and notes:
- Many helpers assert shadow-scale alignment and size multiples; callers that poison allocator memory must honor KASAN alignment contracts.
- `kasan_shadow_check()` suppresses checks while DDB recovery is active to avoid recursive faults in debugger paths.
- DMA uio checking skips non-kernel vmspaces, so user-space DMA buffers are not shadow-validated here.
- Bus write wrappers mark source buffers as `write` in their checks even though CPU-side access is a read from the source buffer; this reflects existing code and should be reviewed carefully before changing because poison semantics may be intentional or historical.
- The file deliberately uses `#undef` to bypass macro interposition and call original primitives; include/order changes can break wrapper binding.
