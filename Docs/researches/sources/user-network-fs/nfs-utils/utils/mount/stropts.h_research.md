<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/stropts.h -->
# sources/user-network-fs/nfs-utils/utils/mount/stropts.h

## Purpose

`stropts.h` exposes the text-option NFS mount entry point used by the command-line mount frontend.

## Important APIs, types, and functions

It declares `nfsmount_string(const char *spec, const char *node, char *type, int flags, char **extra_opts, int fake, int child)`, returning a mount command exit code.

## Control flow

The header has no executable logic. Its declaration transfers control to `stropts.c`, which owns parsing, validation, negotiation, retries, and the final `mount(2)` call.

## State and persistence behavior

The function contract includes an in/out `extra_opts` pointer. Implementations may replace this string with options appropriate for mtab or caller persistence.

## Dependencies and integration points

It is included by `mount.nfs` frontend code. The API exposes only primitive C types, keeping callers insulated from `struct nfsmount_info` and the option-list internals.

## Risks and edge cases

Callers must pass a valid mutable `char **extra_opts`; on success the pointed-to string may be freed and replaced. Misunderstanding `fake` or `child` changes whether mounts are executed or retried as a daemon.

## Test signals

Build coverage should ensure the mount frontend calls this interface with correct argument ownership. Integration tests should verify that `extra_opts` changes are visible to the caller.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/stropts.h -->
