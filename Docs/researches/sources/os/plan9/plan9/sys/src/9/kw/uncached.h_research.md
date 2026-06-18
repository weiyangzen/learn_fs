# File Research: sources/os/plan9/plan9/sys/src/9/kw/uncached.h

## Role

Header that redirects allocation APIs to uncached allocation variants for code that includes it. It provides wrappers for zeroed uncached allocation.

This is memory-allocation support for DMA/device code, not filesystem logic.

## Main Interfaces

- Macro remaps:
  - `free` -> `ucfree`
  - `malloc` -> `myucalloc`
  - `mallocz` -> `ucallocz`
  - `smalloc` -> `myucalloc`
  - `xspanalloc` -> `ucallocalign`
  - `allocb` -> `ucallocb`
  - `iallocb` -> `uciallocb`
  - `freeb` -> `ucfreeb`
- Static helpers:
  - `ucallocz`
  - `myucalloc`

## Important Behavior

- Forces ordinary allocation calls in an including file to use uncached memory.
- `ucallocz` ignores the second argument and allocates zeroed uncached memory.
- `myucalloc` panics on allocation failure.

## Dependencies And Assumptions

- Requires uncached allocation functions declared in `fns.h`.
- Intended for inclusion in specific driver translation units, not globally.

## Notable Risks

- Macro replacement can surprise included code and change ownership/freeing expectations.
- The header creates static functions in each including file.
