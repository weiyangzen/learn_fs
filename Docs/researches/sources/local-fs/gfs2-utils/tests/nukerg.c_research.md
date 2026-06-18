# File Research: sources/local-fs/gfs2-utils/tests/nukerg.c

Test utility that deliberately zeroes selected GFS2 resource group headers and/or rindex entries.

CLI:
- `nukerg -r <num_list>|-i <num_list> /dev/your/device`
- Lists can be comma- or space-separated.
- `*` means all.
- Both `-r` and `-i` may be specified; resource groups are destroyed before rindex entries.

Key functions:
- `parse_uint`, `parse_uint_list`, `parse_ri_list`, `parse_rg_list`, `opts_get`: parse destructive target selections.
- `fill_super_block`: reads GFS2 superblock and master directory through `libgfs2`.
- `read_rindex`: looks up `rindex`, initializes rgrp set, and reads all rindex entries.
- `nuke_rgs`: writes a zeroed `struct gfs2_rgrp` at selected resource group header block offsets.
- `nuke_ris`: writes a zeroed `struct gfs2_rindex` into selected rindex file offsets.
- `main`: validates args, opens device RW, loads metadata, applies destruction, fsyncs and closes.

Dependencies:
- `libgfs2` for superblock, inode, rindex, and rgrp helpers.
- POSIX open/pwrite/fsync/close.

Research notes:
- This is intentionally destructive and exists for corruption/repair tests.
- `parse_rg_list` accepts `str` but calls `parse_uint_list(optarg, ...)`, coupling it to getopt global state.
