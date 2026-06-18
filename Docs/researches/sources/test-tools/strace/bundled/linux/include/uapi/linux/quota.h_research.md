# sources/test-tools/strace/bundled/linux/include/uapi/linux/quota.h

## Purpose

Defines the generic quota control ABI for `quotactl(2)` plus netlink quota-warning attributes. strace uses it to decode quota command composition, quota record structures, quota info flags, and notification messages.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h`. It exports quota type constants `USRQUOTA`, `GRPQUOTA`, `PRJQUOTA`, command composition macros `SUBCMDMASK`, `SUBCMDSHIFT`, and `QCMD`, commands such as `Q_SYNC`, `Q_QUOTAON`, `Q_QUOTAOFF`, `Q_GETFMT`, `Q_GETINFO`, `Q_SETINFO`, `Q_GETQUOTA`, `Q_SETQUOTA`, and `Q_GETNEXTQUOTA`, quota format `QFMT_OCFS2`, and block-size constants. `struct if_dqblk` and `struct if_nextdqblk` carry hard/soft block and inode limits, usage, grace times, validity masks, and ids. `struct if_dqinfo` carries grace periods, flags, and validity. Netlink warning constants and enums describe command and attribute ids for quota notifications.

## Control Flow, State, and Integration

No runtime code is present. Kernel flow is command plus quota type packed by `QCMD`, with filesystem quota state read or mutated depending on command. Persistent state is filesystem quota accounting, limits, grace periods, and notification delivery.

## Risks and Test Signals

Risks include wrong command packing, confusing block-count units with byte-space fields, failing to honor `dqb_valid`/`dqi_valid`, and not decoding `Q_GETNEXTQUOTA`'s id-bearing result. Test signals include `quotactl` decoding for all commands/types, struct field printing with 64-bit usage and limits, validity flag names, and quota netlink warning attributes.
