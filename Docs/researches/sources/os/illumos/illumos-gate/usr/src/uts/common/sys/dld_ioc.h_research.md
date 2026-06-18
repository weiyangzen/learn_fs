# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dld_ioc.h

## Scope

Complete file read, 116 lines. This header defines GLDv3 ioctl command numbering and kernel registration of ioctl handlers.

## Public Surface

It defines:

- `DLD_CONTROL_DEV` as `/dev/dld`.
- `DLD_IOC_CMD(modid, cmdid)` and `DLD_IOC_MODID(cmd)`.
- Module ids for DLD, aggregation, VNIC, simnet, IP tunnel, bridge, IB partition, and overlay.
- Convenience command macros `DLDIOC`, `AGGRIOC`, `VNICIOC`, `SIMNETIOC`, `IPTUNIOC`, `BRIDGEIOC`, `IBPARTIOC`, and `OVERLAYIOC`.

Under `_KERNEL`, it defines:

- `dld_ioc_func_t` and `dld_ioc_priv_func_t`.
- `dld_ioc_info_t`, with command, flags, argument size, handler, and privilege hook.
- Copy flags `DLDCOPYIN`, `DLDCOPYOUT`, `DLDCOPYINOUT`.
- `DLDIOCCNT(l)`.
- `dld_ioc_register()` and `dld_ioc_unregister()`.

## Behavior And Integration

GLDv3 modules register their ioctl handlers with DLD by module id. DLD uses `di_argsize` and copy flags to perform common copyin/copyout before invoking module callbacks.

## Dependencies And Invariants

The 32-bit module id and command id split is fixed at 16 bits each. Modules must use unique module ids and command ids to avoid collisions.

## Risks

Incorrect `di_argsize` or copy flags can cause truncated copies, overreads, or ABI mismatch. Registration lifecycle must match module loading/unloading to avoid dangling handler pointers.
