# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/ss/data.c

## Purpose
`data.c` owns global data for libss.

## Important APIs, Types, and Functions
It defines the MIT copyright string when not linting, the global invocation table `_ss_table`, and default pager name `_ss_pager_name`.

## Control Flow
There is no runtime control flow.

## State, Persistence, Dependencies, Risks, and Test Signals
Persistent process state is `_ss_table`, which indexes active subsystem invocations, and `_ss_pager_name`, which is initialized lazily by pager code. Dependencies are `ss_internal.h`. Risks include global mutable state without locking and sparse index management. Test signals are successful creation/deletion of invocations and pager selection behavior.
