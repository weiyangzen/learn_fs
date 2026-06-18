# sources/sync-backup/borg/docs/usage/with-lock.rst.inc

Purpose: Documents `borg with-lock`, which runs an arbitrary user command while holding the repository lock.

Important APIs/types/functions: CLI contract is `borg [common options] with-lock [options] COMMAND [ARGS...]`. It forwards command arguments and returns the user command's return code as Borg's return code.

Control flow: Runtime acquires the repository lock, executes the subprocess, waits for termination, releases the lock, and exits with the subprocess status. The example wraps `rsync` copying a repository.

State and persistence: Mutates lock state and may allow the child command to read/write external files. Repository data mutation depends entirely on the child command, but the lock serializes Borg-aware access.

Dependencies and integration points: Integrates with Borg repository locking, subprocess execution, `break-lock`, and operational repository copy/maintenance workflows.

Risks: Copying a repository while locked copies the lock too; the copied repository needs `borg break-lock` before use on another host. Subprocess failure must still release the lock.

Test signals: Cover lock acquisition/release, child exit-code propagation, child signal/exception handling, lock contention, and copied-repository stale-lock guidance.
