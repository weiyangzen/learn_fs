# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/symlink.c

## Role

`symlink.c` provides I/O-manager wrappers for creating and deleting object-manager symbolic links, including a protected default form and an unprotected NULL-DACL form.

## Main entry points and behavior

- `IoCreateSymbolicLink()` initializes permanent, kernel-handle, case-insensitive object attributes using `SePublicDefaultSd`, calls `ZwCreateSymbolicLinkObject()`, closes the handle on success, and returns the status (lines 21-45).
- `IoCreateUnprotectedSymbolicLink()` builds a security descriptor with a present NULL DACL, creates the permanent symbolic link with that descriptor, closes on success, and returns the status (lines 50-87).
- `IoDeleteSymbolicLink()` opens the symbolic-link object for `DELETE`, calls `ZwMakeTemporaryObject()` to remove permanence, closes the handle only when that succeeds, and returns the status (lines 92-116).

## Filesystem and device relevance

These wrappers are used by boot and storage code to expose kernel device objects through namespace aliases such as ARC names, DOS device names, and RAM disk links.

## Implementation gaps and risks

- `IoCreateUnprotectedSymbolicLink()` deliberately creates a NULL-DACL object, so callers must ensure the target namespace is intended to be broadly accessible.
- `IoDeleteSymbolicLink()` closes the opened handle only when `ZwMakeTemporaryObject()` succeeds. If `ZwMakeTemporaryObject()` fails after a successful open, the handle is not closed in this implementation (lines 107-112).
