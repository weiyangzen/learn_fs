# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pathname.h

## Purpose
Defines the kernel `pathname_t` abstraction and VFS pathname lookup/manipulation routines used by system calls, symlink expansion, and vnode-to-path conversion.

## Main Interfaces
- `pathname_t`: underlying buffer pointer, current remaining path pointer, remaining length, and total buffer size.
- Pathname buffer/manipulation routines:
  - `pn_alloc()`
  - `pn_alloc_sz()`
  - `pn_get()`
  - `pn_get_buf()`
  - `pn_set()`
  - `pn_insert()`
  - `pn_getsymlink()`
  - `pn_getcomponent()`
  - `pn_setlast()`
  - `pn_skipslash()`
  - `pn_fixslash()`
  - `pn_addslash()`
  - `pn_free()`
- Lookup routines:
  - `lookupname()`
  - `lookupnameat()`
  - `lookupnameatcred()`
  - `lookuppn()`
  - `lookuppnat()`
  - `lookuppnatcred()`
  - `lookuppnvp()`
  - `traverse()`
- Reverse/path discovery helpers:
  - `vnodetopath()`
  - `dogetcwd()`
  - `dirfindvp()`

## Dependencies And Relationships
Includes vnode, credential, uio, and dirent definitions. This is a central VFS pathname resolution contract.

## Research Notes
The convention is that `pn_buf` remains fixed once assigned; path consumption is represented by advancing `pn_path` and updating `pn_pathlen`.
