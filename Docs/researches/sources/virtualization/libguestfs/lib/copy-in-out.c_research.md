# File Research: sources/virtualization/libguestfs/lib/copy-in-out.c

## Role
Implements high-level host-to-guest and guest-to-host recursive copy APIs using tar streams.

## Copy In
- Verifies the local source exists.
- Verifies the remote target is a directory.
- Splits the local path into directory and basename.
- Runs local `tar -cf - <basename>` and passes `/dev/fd/<fd>` to `guestfs_tar_in()`.

## Copy Out
- Verifies the local target directory exists.
- If remote path is a file, downloads it directly to `localdir/basename`.
- If remote path is a directory, starts local `tar -xf -` with a child setup callback that enters `localdir/basename`, then streams `guestfs_tar_out()` into it.
- Handles remote `/` basename as `.`.

## Helper
`split_path()` normalizes trailing slashes and splits path strings into dirname/basename components.

## Filesystem/Storage Relevance
This file provides user-facing recursive file transfer between host filesystems and mounted guest filesystems.
