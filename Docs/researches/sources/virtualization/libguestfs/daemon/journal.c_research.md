# File Research: sources/virtualization/libguestfs/daemon/journal.c

Implements optional systemd journal access.

Important behavior:
- Optional under `HAVE_SD_JOURNAL`.
- Maintains one global `sd_journal *j` and closes it with a destructor.
- `do_journal_open` opens a journal directory under `sysroot_path`.
- Supports close, next, skip forward/backward, threshold get/set, and realtime timestamp retrieval.
- `do_internal_journal_get` streams current entry fields as length-prefixed big-endian blobs using FileOut.

Filesystem relevance: structured log extraction from guest journal directories.
