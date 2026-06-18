# sources/sync-backup/bup/dev/root-status

## Purpose
Reports whether the current process is root, fakeroot, or non-root for tests.

## Important APIs, Types, and Functions
Bootstraps `dev/python`, uses `os.geteuid`, `FAKEROOTKEY`, and Cygwin group IDs 544/0.

## Control Flow
On Cygwin, checks effective group membership for administrator/root-like groups. Else prints `fake` if fakeroot is active, `root` if euid 0, otherwise `none`.

## State and Persistence Behavior
Read-only process credential/environment query.

## Dependencies and Integration Points
Used by tests that branch on root/fakeroot capability.

## Risks and Test Signals
Risks are Cygwin-specific group assumptions and fakeroot env spoofing. Signal is one of `root`, `fake`, or `none`.
