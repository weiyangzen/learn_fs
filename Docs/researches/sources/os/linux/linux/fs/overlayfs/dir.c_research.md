# File Research: sources/os/linux/linux/fs/overlayfs/dir.c

## Role

Implements OverlayFS directory inode operations and upper-layer namespace mutations: create, link, unlink, rmdir, rename, tmpfile, whiteouts, redirects, and opaque directories.

## Main Responsibilities

- Generates temporary workdir names and cleans up temporary objects.
- Manages reusable whiteout inode creation/linking, with fallback when whiteout sharing hits link limits or errors.
- Creates real upper/workdir objects for regular files, directories, special files, symlinks, and hardlinks.
- Marks directories opaque with `OVL_XATTR_OPAQUE`.
- Instantiates overlay dentries/inodes after upper creation or hardlink creation.
- Handles creation over existing upper whiteouts with rename/exchange and ACL restoration.
- Overrides creator credentials so underlying filesystems initialize new inode ownership as the overlay caller expects.
- Implements `create`, `mkdir`, `mknod`, `symlink`, `link`, `unlink`, `rmdir`, `rename`, and `tmpfile`.
- Maintains overlay nlink accounting around hardlink/removal/rename operations.
- Implements redirect xattr creation for renamed merge/lower objects.
- Uses whiteouts to hide lower objects on remove and rename-over.

## Important Control Flow

Creation first copies up the parent, obtains write access, preallocates an overlay inode, initializes owner/mode, then creates or links an upper object under overlay credentials. Creation over whiteout uses a workdir temp object and rename/exchange so the whiteout is replaced atomically.

Removal checks lower presence and directory emptiness, copies up parent, starts nlink accounting, then either removes pure upper entries or replaces lower-visible entries with whiteouts.

Rename starts by validating flags and whether objects can be moved without copying directory trees. It copies up source and parents, possibly copies target for exchange, handles whiteout/overwrite flags, sets redirects or opaque xattrs when required, performs the upper rename, cleans exchanged whiteouts, and updates ctime/nlink state.

## Edge Cases

- Overlay creation of a char-device whiteout is rejected.
- Casefold inheritance for newly created dirs is checked against overlay configuration.
- Directories that become empty may be replaced with opaque temp dirs before cleanup.
- Absolute redirects are used when same-directory relative redirects are insufficient, especially for lower hardlinks.

## Dependencies

Uses VFS rename/create helpers, overlay workdir/upperdir helpers, xattrs, ACL helpers, credential override classes, backing tmpfile APIs, and copy-up/nlink utilities.

## Research Notes

This file is the namespace mutation core of OverlayFS. Whiteout, redirect, opaque, impure, and nlink metadata are all maintained here to make upper-layer changes represent union semantics.
