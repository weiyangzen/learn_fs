# File Research: sources/os/plan9/9front/sys/src/cmd/ip/tftpfs.c

This is a read-only 9P filesystem client for TFTP. It exposes remote TFTP paths as files under a mount point or srv name.

Key behavior:
- Uses libthread and lib9p `Srv`.
- `attach` selects a default or per-attach server IP.
- Walking builds synthetic paths; any path containing a dot is treated as file data.
- Reads/stat on a file spawn or use a `download` process that sends TFTP RRQ packets and caches data.
- ACKs blocks, handles retransmitted blocks, and serves reads while download is in progress.

Research notes:
- File paths with no dot can be forced as files by appending a trailing dot, stripped from the TFTP request.
- Only read/exec opens are allowed.
