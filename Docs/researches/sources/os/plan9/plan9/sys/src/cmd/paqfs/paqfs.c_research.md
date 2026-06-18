# File Research: sources/os/plan9/plan9/sys/src/cmd/paqfs/paqfs.c

Implements a read-only 9P server for `paqfs` archives. It can mount an archive, post a srv file, run on stdio, set cache/message sizes, disable auth-style ownership checks, quiet banner output, and verify the archive SHA1.

Initialization reads and validates the header, optionally streams all blocks for SHA1 verification, reads the trailer, allocates an LRU-ish block cache, and constructs a root `Paq` tree node. If the archived root is a regular file, it synthesizes a containing root directory.

9P support includes version, attach, walk, open, read, clunk, stat, and read-only failures for create/write/remove/wstat. Reads load pointer blocks then data or directory blocks. Directory reads pack serialized `PaqDir` entries into 9P stat records and maintain fid offset state.

`blockLoad` caches blocks by archive byte address with refcounts and age. `blockRead` validates block headers, inflates deflated blocks when needed, and checks Adler-32 against unencoded data.

Permission checks use owner/group/other mode bits, with `-a` allowing username comparisons to pass owner/group checks more broadly.
