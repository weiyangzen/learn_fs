# sources/user-network-fs/samba/source4/ntvfs/common/wscript_build

## Purpose

`source4/ntvfs/common/wscript_build` declares the `ntvfs_common` subsystem containing shared NTVFS support for initialization, byte-range locking, open-file database, and change notification.

## Important APIs, Types, and Functions

It uses `bld.SAMBA_SUBSYSTEM()` with source files `init.c`, `brlock.c`, `brlock_tdb.c`, `opendb.c`, `opendb_tdb.c`, and `notify.c`, and generates `proto.h`.

## Control Flow

At build time it creates one subsystem target named `ntvfs_common` with private dependencies and public dependencies needed by consumers.

## State and Persistence Behavior

The script stores build metadata only. It determines that common runtime state implementations using DB wrappers, NDR records, sys notify, and sys leases are linked together.

## Dependencies and Integration Points

Private dependencies are `util_tdb` and `tdb-wrap`. Public dependencies are `NDR_OPENDB`, `NDR_NOTIFY`, `sys_notify`, `sys_lease`, and `share`, making those interfaces available to downstream NTVFS modules.

## Risks and Edge Cases

Generated `proto.h` freshness matters because `ntvfs_common.h` includes it. Missing public dependencies can break consumers that include the common header but do not link the implementation directly.

## Test Signals

Signals include successful build of `ntvfs_common`, generation of `proto.h`, and downstream NTVFS backends linking against brlock, opendb, notify, sys-notify, and sys-lease symbols.
