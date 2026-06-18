# File Research: sources/os/plan9/9front/sys/src/9/port/dev.c

Generic helper functions for Plan 9 kernel device implementations.

Key behavior:
- `mkqid`, `devno`, and `devdir` build qids and directory metadata.
- Extensive comments document the subtle expectations and contradictions around `Devgen`, `devwalk`, `devstat`, and `devdirread`.
- `devgen` implements table-backed directory generation, with the first table entry representing the directory itself.
- Default `devreset`, `devinit`, and `devshutdown` are no-ops.
- `devattach` creates a root channel for a device spec and constructs its path.
- `devclone` clones unopened channels.
- `devwalk` implements generic walking through a `Devgen`, including cloned-channel ownership and partial-walk behavior.
- `devstat` stats a channel through a generator, fabricating directory stats when needed.
- `devdirread` serializes directory entries from a generator into user buffers.
- `devpermcheck` checks permissions against file owner, `eve`, or other users.
- `devopen` performs generator lookup, permission checks, directory open restrictions, and marks the channel open.
- Default create/remove/wstat/power/config operations reject with `Eperm`.
- `devbread` and `devbwrite` adapt byte-oriented device read/write methods to `Block` I/O.

Notable dependencies:
- Device table, `Chan`, `Dirtab`, `Dir`, `Walkqid`, and Plan 9 directory serialization.
- Global `eve` and current process user.

Research notes:
- The comment block is important API documentation for writing correct device generators.
- `devdirread` treats too-small directory entry serialization as `Eshort` only when no entries have yet been copied.
