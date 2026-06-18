# File Research: sources/os/plan9/plan9/sys/src/9/port/ucallocb.c

## Role

Allocates and frees `Block` network buffers from uncached memory, using `ucalloc` underneath. This is for interrupt/DMA paths that need non-cache-coherent buffers.

## Main Data

`Hdrspc` reserves 64 bytes for prepended higher-level headers. `ucialloc.bytes` tracks interrupt-time uncached block allocation. Freed blocks are poisoned with `Bdead` (`"QIOB"`).

## Control Flow

`_ucallocb` allocates `sizeof(Block)+size+Hdrspc`, initializes the `Block`, aligns data start/end to `BLOCKALIGN`, leaves header slack at the front, and sets `rp`/`wp`. `ucallocb` requires `up != nil`, panics on failure, and tags the allocation. `uciallocb` is the interrupt-allocation variant: it may return nil, marks `BINTR`, and accounts bytes. `ucfreeb` decrements the ref count, calls custom free hooks if present, updates interrupt accounting, poisons pointers, and returns memory to `ucfree`.

## Dependencies

Depends on `Block`, atomic ref helpers `_xinc/_xdec`, `msize`, `ucalloc`, `ucfree`, `setmalloctag`, `conf.ialloc`, and kernel allocation conventions.

## Risks

Normal `ucallocb` panics rather than returning nil. The ialloc limit code is compiled out with `if(0)`. Pointer poisoning helps catch use-after-free but assumes no later legitimate inspection of freed blocks.
