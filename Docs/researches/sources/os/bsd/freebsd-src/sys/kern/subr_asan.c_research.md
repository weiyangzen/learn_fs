# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_asan.c

## Summary
Implements the FreeBSD kernel address sanitizer runtime support. It maps and updates shadow memory, validates compiler-instrumented memory accesses, wraps common kernel memory/usercopy/atomic/bus operations, registers global redzones, and provides ASAN ABI entry points.

## Main Responsibilities
- Initializes KASAN early and normal runtime state through machine-dependent hooks.
- Maps KASAN shadow pages for kernel address ranges.
- Marks valid object bytes and invalid redzones in shadow memory.
- Checks shadow bytes for reads/writes of known and dynamic sizes.
- Reports violations by panic or diagnostic stack trace depending on `debug.kasan.panic_on_violation`.
- Wraps memory/string/usercopy operations so uninstrumented builtins and copy routines still validate kernel buffers.
- Wraps atomic operations from `atomic_san.h` with shadow checks.
- Wraps bus space helpers from `bus_san.h`, checking kernel memory buffers for multi/region transfers.
- Implements compiler ABI hooks such as `__asan_load*`, `__asan_store*`, global registration, stack poisoning, alloca poisoning, and shadow setters.

## Key APIs
- Runtime setup: `kasan_init_early()`, `kasan_init()`, `kasan_shadow_map()`, `kasan_thread_alloc()`.
- Shadow updates: `kasan_mark()`, `kasan_shadow_Nbyte_fill()`, `kasan_shadow_Nbyte_markvalid()`.
- Checked libc-style helpers: `kasan_memcpy()`, `kasan_memcmp()`, `kasan_memset()`, `kasan_memmove()`, `kasan_strlen()`, `kasan_strcpy()`, `kasan_strcmp()`.
- Checked usercopy helpers: `kasan_copyin()`, `kasan_copyinstr()`, `kasan_copyout()`, `kasan_fueword*()`, `kasan_casueword*()`.
- ABI hooks: `__asan_register_globals()`, `__asan_unregister_globals()`, `__asan_load*()`, `__asan_store*()`, `__asan_set_shadow_*()`, `__asan_poison_stack_memory()`, `__asan_unpoison_stack_memory()`, `__asan_alloca_poison()`, `__asan_allocas_unpoison()`.

## Important Behavior
KASAN is disabled by default until `kasan_init()` sees that `debug.kasan.disabled` is not set, runs `kasan_md_init()`, and flips `kasan_disabled` false. Checks also skip zero-size accesses, unsupported machine-dependent address ranges, quieted threads with `TDP2_SAN_QUIET`, and panic state.

Shadow bytes follow the ASAN convention: `0` means a full granule is valid, small positive values mean a partially valid granule, and poison codes identify redzone/use-after-free/stack states. `kasan_code_name()` converts those codes to report labels.

`kasan_mark()` requires kernel addresses aligned to `KASAN_SHADOW_SCALE`, writes full valid granules, an optional partial-granule byte, then redzone poison. It is used for heap-like objects, global redzones, and thread stack marking.

Fast validation paths exist for constant sizes 1, 2, 4, and 8, with boundary-crossing cases decomposed into smaller checks. Dynamic or unusual sizes fall back to byte-by-byte validation.

Global registration poisons bytes after each global's actual size up to `size_with_redzone`; unregistering marks the entire global region valid. Stack and alloca helpers poison compiler-created stack redzones, but `__asan_poison_memory_region()` and `__asan_unpoison_memory_region()` are currently empty stubs.

## Dependencies
Depends on machine-dependent ASAN address translation and initialization (`machine/asan.h`), pmap sanitizer mapping, kernel stack reporting, sysctl/tunable infrastructure, atomic and bus sanitizer headers, usercopy helpers, and compiler ASAN ABI expectations.

## Risks
The runtime is tightly coupled to compiler ASAN ABI version and machine shadow mapping. Shadow marking functions assume alignment and granularity invariants; incorrect sizes can trip assertions or leave false negatives/positives. Some bus write buffer wrappers check source buffers as writes even though semantically they are reads from kernel memory, which is worth reviewing before changing sanitizer policy. Empty poison/unpoison memory-region hooks mean callers expecting those generic ABI hooks to enforce poisoning will not get behavior here.
