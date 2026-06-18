# File Research: sources/os/plan9/9front/sys/src/cmd/paqfs/paqfs.c

## Role

Mounts a `paqfs` archive as a read-only 9P filesystem.

## Startup

`main` parses mount/service/auth/cache/message-size/verify options, calls `init`, then serves 9P over stdio or a pipe mounted at `/n/paq` or posted in `/srv`.

`init` reads and validates the archive header, optionally verifies all blocks and trailer SHA1, initializes an LRU-ish block cache, loads the root `PaqDir`, and handles the special case where the archive root is a regular file by fabricating a directory root containing that file.

## 9P Operations

Implements version, attach, walk, open, read, clunk, stat, and read-only errors for create/write/remove/wstat. Permissions are checked against stored uid/gid/mode, with `-a` allowing no-auth owner/group checks.

Directory reads traverse pointer blocks and directory blocks, packing `Dir` records with `convD2M`. File reads map offsets through the file’s pointer block and load data blocks.

## Archive Access

`blockLoad` caches decoded blocks by byte address, using an age counter and reference counts. `blockRead` seeks to a block, validates magic/type/size, inflates if needed, and checks Adler-32.

The file includes deserializers for archive headers, blocks, trailers, directory entries, strings, and integers.

## Notable Details

The filesystem is strictly read-only. `-v` verifies the entire archive digest before serving; otherwise it seeks directly to the trailer based on file length.
