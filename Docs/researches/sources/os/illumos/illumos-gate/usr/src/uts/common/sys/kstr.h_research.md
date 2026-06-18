# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kstr.h

## Purpose
Defines kernel STREAMS helper operations for opening streams, pushing/popping modules, linking, messaging, ioctls, close, and autopush configuration.

## Main Interfaces
- Autopush operation constants:
  - `SET_AUTOPUSH`
  - `GET_AUTOPUSH`
  - `CLR_AUTOPUSH`
- STREAMS helper APIs:
  - `kstr_open()`
  - `kstr_plink()`
  - `kstr_unplink()`
  - `kstr_push()`
  - `kstr_pop()`
  - `kstr_close()`
  - `kstr_ioctl()`
  - `kstr_msg()`
  - `kstr_autopush()`

## Dependencies And Relationships
Includes `sys/stream.h`, using STREAMS types such as `vnode_t`, `mblk_t`, and `timestruc_t`. This is a kernel interface to STREAMS plumbing operations.

## Research Notes
`kstr_autopush()` operates over major/minor ranges and an array of module names, making this header part of STREAMS configuration machinery as well as runtime stream manipulation.
