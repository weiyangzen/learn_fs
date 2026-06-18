# File Research: sources/local-fs/xfsprogs/db/block.c

Implements cursor movement commands for block addressing: `ablock`, `dblock`, `daddr`, `fsblock`/`fsb`, `rtblock`/`rtbno`, `rtextent`/`rtx`, and `logblock`/`lsb`. `ablock` and `dblock` translate file offsets in the current inode’s attr/data fork through `bmap`; `dblock` also handles directory multi-block mappings and realtime files. Device-relative commands validate input against data, realtime, or log geometry and set the cursor on the appropriate device.

The file also implements `print_block`, a raw hex dump renderer for unstructured data buffers. Important integration points are `set_cur`, `set_rt_cur`, `set_log_cur`, `inode_next_type`, and the bmap extent helpers. It contains rtgroup-aware realtime block validation and distinguishes internal vs external logs.
