# File Research: sources/local-fs/jfsutils/logdump/logdump.c

Command-line front end for dumping a JFS journal log. It prints version information, parses options, opens the target block device read-only, and calls external `jfs_logdump(...)`.

Important behavior:
- Supports `jfs_logdump [-a] <block device>`.
- `-a` or `-A` sets `dump_all = -1`, requesting a full log dump instead of only committed transactions since the last sync point.
- Device arguments must begin with `/`; otherwise parsing rejects them.
- Stores the selected device in global `Vol_Label`.
- Opens the device with `fopen(Vol_Label, "r")`, calls `jfs_logdump(Vol_Label, Dev_IOPort, dump_all)`, then closes it.

Globals:
- `Dev_IOPort`, `Dev_blksize`, `Vol_Label`, `dump_all`.
- Defines dummy `log_device[1]` to avoid a linker error.
- Sets external `prog` to `"jfs_logdump"` for message handling.

Filesystem relevance: entry point for reading and decoding JFS journal/log structures through shared libfs/logredo routines.
