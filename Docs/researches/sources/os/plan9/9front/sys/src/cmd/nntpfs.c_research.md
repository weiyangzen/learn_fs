# File Research: sources/os/plan9/9front/sys/src/cmd/nntpfs.c

A 9P filesystem view of an NNTP server.

Key elements:
- `Netbuf` tracks NNTP I/O, auth state, current group, server address, credentials, and extension flags.
- `Group` builds a tree from dotted newsgroup names with range, posting, and timestamp metadata.
- Connects to NNTP, optionally authenticates with `AUTHINFO USER/PASS`, and refreshes groups via `LIST`.
- Caches `XOVER` results in 100-message chunks for overview reads.
- Maps group hierarchy, article directories, and article files (`header`, `body`, `article`, `xover`) into 9P.
- Supports a writable `post` file in postable groups; writing zero bytes commits with NNTP `POST`.
- Uses QID path bits for group/message and QID version bits for per-message file kind.
- Refreshes root/group metadata on stat/read with rate limiting for groups.

Notable behavior:
- Article data is fetched lazily through `HEAD`, `BODY`, `ARTICLE`, or `XOVER`.
- Read offsets over directories use an auxiliary offset cache.
- `fsdestroyfid` auto-posts pending post content when a post fid is destroyed.

Risks and quirks:
- Extension probing is present but disabled/commented.
- The QID encoding limits group/message ID bit widths.
- Posting on fid destroy can surprise callers if they expected explicit zero-length commit only.
