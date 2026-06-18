# sources/test-tools/xfstests/tests/generic/478

## Purpose
Test OFD lock. fcntl F_OFD_SETLK to set lock, then F_OFD_GETLK to verify we are being given correct advice by kernel. OFD lock combines POSIX lock and BSD flock: + does not share between threads + byte granularity (both tested by LTP/fcntl3{4,6}) + only release automatically after all open fd closed This test target the third one and expand a little bit. The basic idea is one setlk routine setting locks via fcntl *_SETLK, followed by operations like clone, dup then close fd; another routine getlk getting locks via fcntl *_GETLK. Firstly in setlk routine process P0, place a lock L0 on an opened testfile, then + clone() a child P1 to close the fd then tell getlk to go, parent P0 wait getlk done then close fd. or + dup() fd to a newfd then close newfd then tell getlk to go, then wait getlk done then close fd. In getlk process P2, do fcntl *_GETLK with lock L1 after get notified by setlk routine. In the end, getlk routine check the returned struct flock.l_type to see if the lock mechanism works fine. When testing with clone, + CLONE_FILES set, close releases all locks; + CLONE_FILES not set, locks remain in P0; If L0 is a POSIX lock, + it is not inherited into P1 + it is released after dup & close If L0 is a OFD lock, + it is inherited into P1 + it is not released after dup & close setlk routine: * getlk routine: start * start | * | open file * open file | * | init sem * | | * | wait init sem done * wait init sem done | * | setlk L0 * | | * | |---------clone()--------| * | | | * | |(child P1) (parent P0)| * | (P2) | | * | | close fd * | | | * | | set sem0=0 * wait sem0==0 | | * | | | * getlk L1 | | * | wait sem1==0 | * set sem1=0 | | * | exit wait child * | | * check result cleanup * | | * | exit * exit We can test combainations of: + shared or exclusive lock + these locks are conflicting or not + one OFD lock and one POSIX lock + that open testfile RDONLY or RDWR + clone with CLONE_FILES or not + dup and close newfd. It is registered as generic/478 with `_begin_fstest` tags `auto, quick`, making it part of the locking semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: mk_sem, rm_sem, do_test. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: locking semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions mk_sem, rm_sem, do_test.

## State and Persistence Behavior
uses persistent files under TEST_DIR.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_ofd_locks.

External/helper commands: $XFS_IO_PROG, grep.

Representative `xfs_io` operations: pwrite -S 0xFF 0 4096.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior.

## Test Signals
The golden `.out` expects normalized signals such as: get wrlck; lock could be placed; get wrlck; get wrlck; lock could be placed; get wrlck. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.
