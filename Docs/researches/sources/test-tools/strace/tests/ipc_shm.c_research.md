<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_shm.c -->
# sources/test-tools/strace/tests/ipc_shm.c

Purpose: Tests SysV shared-memory decoding for `shmget` and `shmctl`, including huge-page flags, metadata structures, attach/detach fields, and Linux info/stat commands.

Important APIs/types/functions: Uses `shmget`, `shmctl`, `struct shmid_ds`, `struct shm_info`, `struct shminfo`, cleanup with `IPC_RMID`, xlat table `shm_resource_flags`, and helpers that print decoded structures.

Control flow: Builds bogus keys/flags including `SHM_HUGETLB`, `SHM_NORESERVE`, and huge-page shift bits, creates a private shared-memory segment, conditionally checks bogus command/address behavior, prints IPC/stat/info variants, updates permissions through `IPC_SET`, and removes the segment during cleanup.

State/persistence behavior: Creates one SysV shared-memory segment and removes it with `atexit(cleanup)`. No persistent memory object should remain after a normal run.

Dependencies: Requires SysV shared memory, UAPI flag availability with local fallbacks, glibc-version guards, and xlat data for shared-memory resource flags.

Integration points: Validates strace formatting of shared-memory flags, huge-page expressions, permission/time fields, process ids, attachment counts, and command xlat modes.

Risks: libc invalid-command behavior varies; system IPC limits or permissions can skip/fail setup. Huge-page flag formatting is easy to regress because it mixes named bits with shifted size encodings.

Test signals: Expected output includes bogus `shmget`, private segment id, decoded `shmctl` structures, cleanup, and xlat-mode-specific command rendering.

Source read signal: complete file read for this research pass; file size 323 line(s), 9494 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_shm.c -->
