# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_loginclass.c

## Purpose
Maintains login class objects and implements `setloginclass(2)` and `getloginclass(2)`. Login classes are attached to credentials and used by RACCT/RCTL for per-class resource accounting and limits.

## Key Interfaces
- `loginclass_hold()` and `loginclass_free()` manage refcounts.
- `loginclass_find()` returns an existing or newly created class by name.
- `sys_getloginclass()` copies the current credential login class name to userspace.
- `sys_setloginclass()` replaces the process credential login class after privilege checks.
- `loginclass_racct_foreach()` iterates login class RACCT objects under the list lock.

## State And Locking
Global `loginclasses` is protected by `loginclasses_lock`. Each `struct loginclass` has a name, refcount, RACCT pointer, and list linkage. Allocation is race-safe: lookup is retried under write lock after memory allocation to avoid duplicate class insertion.

## Control Flow
Lookup first checks the current credential's class, then scans the global list, then allocates a new class and inserts it if still absent. `setloginclass` checks `PRIV_PROC_SETLOGINCLASS`, copies the requested name, resolves the class, creates a new credential, swaps it into the process, updates RACCT/RCTL state when compiled in, and releases the old credential and old login class.

## Integration Notes
Depends on credentials, process locking, privilege checks, RACCT, RCTL, refcounts, and rwlocks. Empty names and names at least `MAXLOGNAME` are rejected.

## Risks
Credential replacement has distinct RACCT and RCTL hooks; changes here must preserve reference ownership around `proc_set_cred()`. `loginclass_free()` uses a fast refcount release path and then a locked last-reference path to safely remove classes from the global list.
