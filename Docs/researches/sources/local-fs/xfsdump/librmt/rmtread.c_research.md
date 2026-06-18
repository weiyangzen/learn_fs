# File Research: sources/local-fs/xfsdump/librmt/rmtread.c

Implements `rmtread(fildes, buf, nbyte)`.

Behavior:
- Local descriptors call `read(2)`.
- Remote descriptors send `R<nbyte>\n`, read status as byte count, then read that many bytes from the remote pipe.
- On pipe read failure, aborts and sets `errno = EIO`.

Notable implementation detail:
- The read loop mutates `nbyte` to the last read count and passes `rc` as the requested size each time; this still aims to accumulate `rc` bytes but is awkward and depends on short-read behavior not causing overread into the destination.
