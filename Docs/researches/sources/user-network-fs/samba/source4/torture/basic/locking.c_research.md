# sources/user-network-fs/samba/source4/torture/basic/locking.c

## Purpose
This file builds the `lock` torture suite for SMB byte-range locking semantics. It checks close behavior, lock timeouts, PID-scoped contexts, 32-bit offsets, overlapping read/write locks, recursive lock stacks, unusual LockingX bits, strict locking enforcement, and truncation while locked.

## Important APIs, types, and functions
The suite is created by `torture_base_locktest()`, registering `LOCK1` through `LOCK7`. Local tests are `torture_locktest1()` through `torture_locktest7()`. They use `smbcli_open()`, `smbcli_close()`, `smbcli_lock()`, `smbcli_unlock()`, `smbcli_locktype()`, `smbcli_read()`, `smbcli_write()`, `smbcli_getatr()`, `smbcli_unlink()`, and `check_error()`. `cli->session->pid` is deliberately mutated to simulate multiple SMB process IDs over one connection.

## Control flow
`LOCK1` verifies locks persist until the locking handle closes and that timed lock requests actually wait. `LOCK2` checks same-connection PID isolation and failed unlocks from the wrong PID. `LOCK3` walks offsets across the 32-bit range and verifies non-overlap and conflict behavior. `LOCK4` probes overlapping read/write combinations across same process, different connection, and different PID, including strict read/write blocking and a known NT byte-range bug. `LOCK5` focuses on lock upgrade/downgrade and stack unlock order. `LOCK6` sends `LOCKING_ANDX_CHANGE_LOCKTYPE` and `LOCKING_ANDX_CANCEL_LOCK`. `LOCK7` validates read-lock versus write-lock access restrictions and confirms truncation through a separate open.

## State and persistence
All test files live under `\locktest` except `LOCK6`'s `\lock6.txt`. The persistent server state under test is lock ownership by connection, PID, fnum, range, and lock type. There is no local durable state.

## Dependencies and integration points
The suite depends on the basic torture framework and connected one- or two-SMB test wrappers. It validates Samba behavior against Windows/SMB semantics rather than POSIX byte-range lock semantics, especially same-PID overlap rules.

## Risks
Timing-sensitive checks can fail on very slow or overloaded servers. Tests mutate `cli->session->pid` and must leave it sane for later operations. Some cases intentionally call unlocks after failed locks to probe behavior, so error handling must be read in context.

## Test signals
Important signals are expected `ERRlock`, `ERRnotlocked`, `NT_STATUS_LOCK_NOT_GRANTED`, `NT_STATUS_FILE_LOCK_CONFLICT`, and `NT_STATUS_RANGE_NOT_LOCKED`; timed locks sleeping long enough; read/write failures on locked ranges; and the final suite registration exposing all seven cases.
