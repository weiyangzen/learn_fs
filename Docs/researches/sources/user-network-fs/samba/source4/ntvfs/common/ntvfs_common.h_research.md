# sources/user-network-fs/samba/source4/ntvfs/common/ntvfs_common.h

## Purpose

`ntvfs_common.h` is the aggregate public header for source4 NTVFS common services. It exposes common notify, byte-range lock, and open-database interfaces to NTVFS backends.

## Important APIs, Types, and Functions

It forward-declares `struct notify_event` and `struct notify_entry`, includes `ntvfs/ntvfs.h`, `brlock.h`, `opendb.h`, and generated `proto.h`.

## Control Flow

The header has no executable control flow. It organizes declarations so modules can include one common header for brlock, opendb, notify, and subsystem initialization prototypes.

## State and Persistence Behavior

The header itself has no state. It exposes opaque context and lock types whose implementations persist runtime state in temp cluster databases.

## Dependencies and Integration Points

It is included by `brlock.c`, `brlock_tdb.c`, `opendb.c`, `opendb_tdb.c`, `notify.c`, and NTVFS backends. It binds the common subsystem's generated prototypes into consumers.

## Risks and Edge Cases

As an aggregate header, changes can increase rebuild scope or introduce include cycles. Generated `proto.h` must stay synchronized with implementation exports.

## Test Signals

Compile-time coverage from all NTVFS common and backend targets is the primary signal. Include-order tests are useful because this header pulls together several interfaces.
