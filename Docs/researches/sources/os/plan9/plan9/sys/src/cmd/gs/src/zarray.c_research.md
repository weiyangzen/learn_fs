# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zarray.c

Implements core PostScript array operators `array`, `aload`, and `astore`; generic array operators are delegated to `zgeneric.c`.

Key behavior:
- `array` validates requested size against `max_array_size`, allocates a ref array with `ialloc_ref_array`, and initializes all slots to null.
- `aload` supports normal and packed arrays. If the current operand stack segment lacks room, it uses `ref_stack_push` and `packed_get` to handle segmented stacks safely.
- `astore` validates writable arrays, stores operand-stack values into the target array, and handles cross-stack-segment stores with `ref_stack_store`.
- For same-segment `astore`, it uses `refcpy_to_old` to preserve VM write-barrier behavior.

Dependencies and coupling:
- Uses interpreter allocator APIs (`ialloc.h`), packed array support (`ipacked.h`), ref-stack utilities, and VM-aware store helpers.
- Important for GC correctness because array writes use old-object assignment helpers.
