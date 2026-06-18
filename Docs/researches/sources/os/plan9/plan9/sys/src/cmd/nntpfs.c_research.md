# File Research: sources/os/plan9/plan9/sys/src/cmd/nntpfs.c

Implements an NNTP-backed 9P file server mounted by default at `/mnt/news`. It presents NNTP newsgroup hierarchy as directories, article numbers as subdirectories, and article parts as files named `header`, `body`, `article`, and `xover`.

`Netbuf` wraps the NNTP connection, buffered I/O, response state, optional authentication, and current group. NNTP helpers handle reconnecting commands, response validation, AUTHINFO, group refresh, XOVER chunk caching, article retrieval, and posting.

`Group` forms a sorted hierarchy split on dots. Root refresh uses `LIST`; per-group refresh uses `GROUP` with a 30-second access-time throttle. Qid encoding packs group and article numbers into limited path/version bits.

The 9P server supports attach, walk, open, read, write-to-post, stat, clone, and destroyfid. Directories are synthesized from group children, post file, and article-number ranges. Posting writes accumulate in fid aux state and are submitted on zero-length write or fid destroy.

Authentication uses Plan 9 auth key lookup when `-a` is supplied, optionally with `-u user`. Debug flags include 9P and network command tracing.
