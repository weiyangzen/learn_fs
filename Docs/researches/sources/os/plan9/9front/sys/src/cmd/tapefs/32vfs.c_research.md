# File Research: sources/os/plan9/9front/sys/src/cmd/tapefs/32vfs.c

`32vfs.c` is a `tapefs` backend for VAX 32V Unix filesystems, also noting pre-FFS Berkeley compatibility.

Format support:
- Disk inode has 13 three-byte block addresses, 16-bit ids/mode, 32-bit size and times.
- Directory entries are 2-byte inode plus 14-byte name.
- Default block size is 512; `-b 1024` supports 4.1BSD-style block size.

Backend callbacks:
- `populate` opens the image, reads root inode 2, and initializes root `ram`.
- `popdir` lazily reads directory entries and creates child `Ram` nodes with `popfile`.
- `doread` maps file offsets through logical block numbers and static block buffer.
- `iget` reads an inode and converts it into `Fileinf`.
- `bmap` handles direct blocks and singly indirect blocks only.
- Write/truncate/create callbacks are no-ops; `dopermw` denies writes.

Risks:
- Explicitly lacks deeper indirect block support.
- Minimal sanity checking; bad images can trigger fatal reads or odd metadata.
- Uses static read buffer, so concurrent reads would not be reentrant.
