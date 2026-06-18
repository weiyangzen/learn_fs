# File Research: sources/os/plan9/plan9/sys/src/9/mtx/devarch.c

## Role

MTX architecture device implementation, exposing architecture-specific files and managing I/O port allocation. It implements the `#P/arch` device table used to inspect and mutate low-level machine state.

This is platform device support, not filesystem implementation, though it exposes a Plan 9 device namespace.

## Main Interfaces

- `addarchfile`
- `ioinit`
- `ioalloc`
- `iofree`
- `iounused`
- Device operations:
  - `archattach`
  - `archwalk`
  - `archstat`
  - `archopen`
  - `archclose`
  - `archread`
  - `archwrite`
- PCMCIA stubs:
  - `pcmspecial`
  - `pcmspecialclose`

## Data Structures

- `IOMap`: linked list node describing allocated or free I/O port ranges.
- `archdir[]`: dynamic architecture file directory entries.
- `readfn[]` and `writefn[]`: per-arch-file callbacks.

## Important Behavior

- Tracks I/O port ownership with a sorted linked list.
- `ioalloc` supports explicit port ranges or dynamic allocation with alignment.
- `iofree` releases exact ranges.
- Architecture files can be added dynamically with callbacks.
- Device read/write dispatches based on QID path and callback arrays.

## Dependencies And Assumptions

- Uses Plan 9 `Dev`/`Chan`/`Dirtab` conventions.
- Assumes x86-like I/O port concepts for this platform layer.

## Notable Risks

- I/O range allocation is manually managed and can fragment.
- `checkport` raises errors for invalid ranges, so callers must validate hardware claims.
