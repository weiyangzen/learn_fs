# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pathname.c

## Purpose
Provides kernel pathname buffer utilities used during path lookup and symlink expansion.

## Main Entry Points
- `pn_alloc()` and `pn_alloc_sz()` allocate pathname buffers.
- `pn_free()` frees pathname storage.
- `pn_get_buf()` copies a user or kernel string into a caller-provided pathname buffer.
- `pn_get()` allocates a `MAXPATHLEN` buffer and copies a pathname into it.
- `pn_set()` resets an allocated pathname to a kernel string.
- `pn_insert()` replaces the current component with symlink contents during lookup.
- `pn_getsymlink()` reads a symlink target into a pathname buffer.
- `pn_getcomponent()` extracts the next path component.
- `pn_skipslash()`, `pn_setlast()`, `pn_fixslash()`, and `pn_addslash()` manipulate slash and component state.

## Internal Mechanics
`struct pathname` tracks the original buffer, current path pointer, current path length, and buffer size. `pn_get_buf()` supports user-space and kernel-space sources via `copyinstr()` and `copystr()`, then subtracts the terminating NUL from `pn_pathlen`.

`pn_insert()` is designed for symlink processing. Absolute symlink targets replace the entire pathname buffer from the start. Relative targets replace the just-consumed component by moving `pn_path` backward by `complen` and inserting the target before the remaining suffix.

`pn_getcomponent()` temporarily writes a slash sentinel at either `MAXNAMELEN` or current path length to guarantee loop termination, copies the component, restores the original byte/NUL, advances `pn_path`, and updates `pn_pathlen`.

Slash helpers trim leading slashes, isolate the final component, remove trailing slashes, or append a trailing slash while compacting the active component to the start of the buffer if needed.

## Dependencies
Uses kernel allocation, copyin/copystr helpers, vnode `VOP_READLINK`, `uio`/`iovec`, and pathname/vnode constants such as `MAXPATHLEN` and `MAXNAMELEN`.

## Risks and Notes
- Many routines mutate the pathname buffer in place and depend on `pn_path`/`pn_pathlen` staying consistent.
- `pn_insert()` and `pn_addslash()` use overlapping copies to preserve remaining path suffixes.
- Component extraction enforces `MAXNAMELEN`; too-long components return `ENAMETOOLONG`.
