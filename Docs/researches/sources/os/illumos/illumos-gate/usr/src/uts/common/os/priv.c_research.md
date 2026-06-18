# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/priv.c

## Purpose

`priv.c` implements the kernel privilege-set abstraction: privilege initialization, `/proc` privilege export/import support, runtime privilege name allocation, opaque set operations, process credential permission checks, and privilege-aware credential flag transitions.

Read completely: 745 lines.

## Main Responsibilities

- Initializes privilege metadata, full/basic/unsafe sets, optional debug privilege allocation, and device policy.
- Converts credentials to and from `prpriv_t` structures used by `/proc`.
- Enforces constraints for setting another process's privilege sets through `priv_pr_spriv()`.
- Exposes privilege implementation info with read locking.
- Maps privilege names to numbers and numbers to names, including dynamic allocation of new privilege names.
- Implements opaque privilege set operations: empty, fill, add, delete, membership, equality, subset, union, intersection, inverse.
- Checks whether one credential may inspect or modify another process's credentials.
- Manages `PRIV_AWARE`, `PRIV_AWARE_RESET`, and related UID-root privilege compatibility behavior.

## Important Data Structures And Globals

- `privinfo_lock`: protects mutable privilege table metadata (`nprivs`, `priv_max`, `priv_names`, name strings).
- `priv_fullset`: set with all privilege bits set.
- `priv_unsafe`: generated set of privileges unsafe for setuid-root exec if absent from the limit set.
- Generated globals from `priv_const.c`: `priv_names`, `priv_setnames`, `nprivs`, `priv_info`, `priv_ninfo`, `priv_str`, `priv_basic`, and sizing fields.

## Control Flow And Algorithms

`priv_init()` initializes the lock, asserts generated basic/unsafe sets, fills the full set, optionally allocates `basic_test`, and initializes device policy.

`cred2prpriv()` writes all kernel privilege sets and privilege info into a `prpriv_t`. `priv_pr_spriv()` validates dimensions, obtains permission to modify the target process, duplicates credentials, copies requested sets, verifies new sets are subsets of old sets or of the acting process's effective authority, rejects limit-set growth, validates `E <= P`, applies permitted info flags, adjusts privilege-aware mode, and swaps credentials under `p_crlock`.

`priv_getbyname()` first scans under a reader lock, optionally upgrades to a writer lock for `PRIV_ALLOC`, validates name length/characters, checks space, copies the new name into the generated string table's slack area, uses a producer memory barrier, updates counts, and returns the new privilege number.

`priv_proc_cred_perm()` holds the target credential, checks zone permission, read/write mode, owner policy, effective-set dominance over target inheritable/permitted sets, and limit-set superset requirements.

`priv_set_PA()`, `priv_adjust_PA()`, and `priv_reset_PA()` implement transitions between legacy UID-root semantics and privilege-aware semantics, adjusting effective/permitted sets relative to inheritable and limit sets.

## Dependencies And Integration

- Uses generated privilege constants and metadata from `privs.awk` output.
- Integrates with credentials (`cred_impl.h`), `/proc`, security policy functions, process locks, zones, and device policy.
- Called from credential initialization and process-control paths.

## Locking And Concurrency

Privilege metadata updates use `privinfo_lock`. `priv_getbynum()` avoids locking and relies on memory barriers so name strings are visible before `nprivs` is increased. Process credential permission and replacement use `p_crlock`; process-state checks often require `p_lock`.

## Notable Risks And Invariants

- Valid credentials must satisfy effective privileges as a subset of permitted privileges.
- `priv_pr_spriv()` must not allow limit-set growth through `/proc`.
- Runtime privilege allocation has finite name and bit capacity.
- Dynamic privilege names are globally visible only after string publication and memory ordering.
- Privilege-aware flag adjustment is sensitive to UID transitions involving UID 0.

## Research Relevance

Kernel privilege checks gate many filesystem and storage operations, including mount, device, process-control, scheduling, and resource-management actions. This file defines the low-level set algebra and credential dominance rules those checks rely on.
