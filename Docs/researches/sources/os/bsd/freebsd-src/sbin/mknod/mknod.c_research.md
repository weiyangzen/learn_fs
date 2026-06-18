# File Research: sources/os/bsd/freebsd-src/sbin/mknod/mknod.c

## Summary
Implements the `mknod` utility for creating character or block device nodes and optionally setting owner/group.

## Main Responsibilities
- Supports `mknod name` for a default character node with device number 0.
- Supports `mknod name [b|c] major minor [owner:group]`.
- Parses major/minor numbers and validates that `makedev()` preserves them.
- Resolves owner and group names or numeric IDs.
- Calls `mknod()` and optional `chown()`.

## Key Functions
- `id()`: parses numeric uid/gid fallback.
- `a_uid()` / `a_gid()`: resolve user/group names or numeric IDs.
- `main()`: validates arguments, constructs mode/dev, creates node, changes ownership.

## Research Notes
The owner/group parser requires both owner and group when the optional sixth argument is present; partial forms are rejected.
