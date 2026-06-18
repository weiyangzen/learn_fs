# File Research: sources/local-fs/reiserfsprogs/debugreiserfs/debugreiserfs.8.in

Manual page template for `debugreiserfs`.

Documents primary modes:
- Default: print filesystem superblock.
- `-j device`: print journal contents.
- `-J`: print journal header.
- `-d`: print formatted tree nodes.
- `-D`: print formatted used blocks.
- `-m`: print bitmap.
- `-o`: print objectid map.
- `-B file`: extract internal bad-block list.
- `-1 block`: print one filesystem block.
- `-p`: pack filesystem metadata to stdout.
- `-u`: unpack packed metadata into an image.
- `-S`: scan entire device instead of bitmap-used blocks.
- `-q`: quiet progress output.
- `-V`: version.

Important behavioral note: `-p` is intended to pack metadata, not file contents, except when corrupt blocks must be copied whole. `-u` recreates filesystem structure from that metadata but not necessarily original data.

Author listed: Vitaly Fertman.
