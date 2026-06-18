# File Research: sources/virtualization/libguestfs/daemon/sleuthkit.c

Wraps Sleuth Kit extraction commands.

Important behavior:
- `do_download_inode` validates non-negative inode and streams `icat -r <device> <inode>`.
- `do_download_blocks` validates start/stop range and streams `blkls`.
- Shared `send_command_output` uses `popen`, sends FileOut reply first, streams chunks, and cancels on read/process errors.
- Optgroup availability checks `icat`.

Filesystem relevance: forensic extraction of inode and block ranges from filesystems without mounting them normally.
