# File Research: sources/os/plan9/9front/sys/src/cmd/tapefs/v6fs.c

`v6fs.c` is a `tapefs` backend for old Unix V6 and earlier PDP-11 filesystems.

Format:
- 512-byte blocks.
- Root inode is 1.
- Inode has 8 two-byte addresses, byte uid/gid, split high/low size, and PDP-11-order timestamps.
- Directory entries are two-byte inode plus 14-byte name.
- Uses the V6 large-file flag indirectly by size: if `r->ndata <= V6NADDR * BLSIZE`, direct addresses are used; otherwise indirect blocks are used.

Behavior:
- `populate` opens the image and seeds root metadata from `iget(V6ROOT)`.
- `popdir` lazily enumerates directory entries and inserts child `Ram` nodes.
- `doread` reads mapped blocks into a static buffer.
- `iget` converts V6 inode fields into `Fileinf`.
- `bmap` maps small direct files or singly indirect large files.
- Write callbacks are denied/no-op.

Risks:
- Large-file detection by size is a heuristic.
- No double-indirect support.
- Minimal image validation and static buffers.
