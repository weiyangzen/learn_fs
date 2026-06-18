# File Research: sources/os/plan9/9front/sys/src/cmd/paqfs/paqfs.h

## Role

Defines the `paqfs` on-disk format shared by the archive builder and filesystem server.

## Main Contents

Constants define header, block, trailer magic values, serialized sizes, version, block-size bounds, minimum directory entry size, block types, and encodings.

Structures include:

- `PaqHeader`: magic, version, block size, creation time, label.
- `PaqBlock`: magic, stored size, type, encoding, Adler-32 of unencoded data.
- `PaqTrailer`: magic, root block offset, SHA1 digest.
- `PaqDir`: qid, mode, mtime, length, pointer block offset, name, uid, gid.

## Format Notes

Blocks are typed as directory, data, or pointer blocks. Encodings are none or deflate. Multi-byte fields are serialized manually in big-endian order by the implementation files.
