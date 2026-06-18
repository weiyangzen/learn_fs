# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sodirect.h

## Purpose
Defines the per-socket sodirect state and declares the async direct-copy receive helpers used by sockfs.

## Key Elements
`sodirect_t` contains an enable flag, a pending-free mblk chain head and tail, and an embedded `uioa_t` for active async copyout state. Macros include `SOD_DISABLE`, `SOD_SOTOSODP`, and `SOD_UIOAFINI`, which flips an enabled uioa state to finalization.

The header declares setup/teardown (`sod_init`, `sod_sock_init`, `sod_sock_fini`), receive lifecycle (`sod_rcv_init`, `sod_rcv_done`), and mblk scheduling/completion helpers (`sod_uioa_mblk_init`, `sod_uioa_so_init`, `sod_uioa_mblk`, `sod_uioa_mblk_done`).

## Dependencies
Depends on `sonode`, `mblk_t`, `uio_t`, and `uioa_t` definitions from the socket/STREAMS/uio layers.

## Behavior/Risks
The macros directly mutate state and assume callers already hold the right socket locks or are in a safe receive path. Misuse can leave async copyout enabled after the receive path has decided to finalize, causing copied mblks to be handled twice or leaked.
