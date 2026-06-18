# File Research: sources/os/linux/linux/mm/kmsan/instrumentation.c

## Role

Implements the compiler-facing `__msan_*` API emitted by Clang for `-fsanitize=kernel-memory`. It returns metadata pointers for instrumented loads/stores, handles compiler-rewritten memory intrinsics, creates stack-local origins, and emits KMSAN warnings.

## Metadata Pointer Hooks

- `__msan_metadata_ptr_for_load_n()` and `__msan_metadata_ptr_for_store_n()` handle non-standard access sizes.
- Macro-generated hooks handle fixed-size loads and stores for 1, 2, 4, and 8 bytes.
- All metadata pointer retrieval uses `user_access_save()` / `user_access_restore()` around `kmsan_get_shadow_origin_ptr()`.
- Bad asm/user/untracked addresses are redirected away from real metadata by lower-level dummy metadata behavior.

## Inline Assembly

- `__msan_instrument_asm_store()` unpoisons memory written by inline assembly on a best-effort basis.
- It intentionally omits the runtime-recursion check so entry/exit assembly stores can be marked initialized.
- Stores larger than 4096 bytes warn once and are clamped to 8 bytes.

## Memory Intrinsics

- `__msan_memmove()` calls `__memmove()`, copies metadata with memmove semantics, and restores return-value metadata from destination parameter metadata.
- `__msan_memcpy()` calls `__memcpy()` and then uses memmove-style metadata copying for correctness.
- `__msan_memset()` calls `__memset()` and unpoisons the destination, because Clang does not pass metadata for the fill byte.
- Zero-length memmove/memcpy calls return without metadata work.

## Origin and Stack Local Handling

- `__msan_chain_origin()` wraps `kmsan_internal_chain_origin()` under runtime and user-access guards.
- `__msan_poison_alloca()` creates an alloca-origin stack-depot record containing a magic value, local variable description, and caller return addresses, then poisons the stack variable.
- `__msan_unpoison_alloca()` clears metadata for stack locals.
- `__msan_warning()` reports undefined use of an uninitialized value.
- `__msan_get_context_state()` returns the current context state holding parameter and return-value TLS metadata.

## Dependencies

Uses KMSAN context state, stack depot, user access helpers, KMSAN string/intrinsic wrappers, and compiler-generated calling conventions.

## Research Notes

This file is the required ABI between compiler instrumentation and the kernel runtime. Its correctness depends on preserving parameter/return metadata through rewritten intrinsics, avoiding recursive runtime instrumentation, and creating meaningful origins for uninitialized stack locals.
