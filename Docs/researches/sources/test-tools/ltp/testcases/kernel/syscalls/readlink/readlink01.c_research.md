# sources/test-tools/ltp/testcases/kernel/syscalls/readlink/readlink01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/readlink/readlink01.c` is a 90-line LTP source file in the `readlink` syscall test area. readlink coverage for symlink target reads, access through changed credentials, and pathname error handling. Source description: Ported to LTP: Wayne Boyer

## Important APIs, Types, and Functions

called APIs/macros: `readlink`, `SAFE_CLOSE`, `SAFE_FORK`, `SAFE_GETPWNAM`, `SAFE_OPEN`, `SAFE_SETUID`, `SAFE_SYMLINK`, `TEST`; local functions: `test_readlink`, `verify_readlink`, `setup`; struct/table types referenced: `struct passwd`, `struct tst_test`; important macros/constants: `TESTFILE`, `SYMFILE`.

## Control Flow

Function-level flow is organized around `test_readlink`, `verify_readlink`, `setup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Some flow is concurrent: child processes or pthreads are used to exercise server, signal-delivery, or permission behavior, with waits/checkpoints joining the result. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is temporary filesystem state created under the LTP scratch directory or mounted test device: files, directories, symlinks, xattrs, descriptors, and pathnames are mutated and then removed. The test expects root privileges or temporarily changes credentials/capabilities.

## Dependencies and Integration Points

Direct includes: `<pwd.h>`, `<errno.h>`, `<string.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.test`, `.tcnt`, `.setup`, `.forks_child`, `.needs_root`, `.needs_tmpdir`.

## Risks and Edge Cases

permission cases depend on credentials, capabilities, and filesystem mode bits; signal or child-process synchronization must avoid races

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `readlink() on %s failed`; `readlink() returned value %ld `; `did't match, Expected %d`; `readlink() functionality on '%s' was correct`.
