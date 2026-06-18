# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/main_mkfs.c

Primary implementation of `mkfs.gfs2`. It parses CLI options, opens and probes the target device, chooses filesystem geometry, creates journals/resource groups, builds core metadata files, writes the superblock, syncs, and prints the final summary.

Key local types are `struct mkfs_dev`, which stores file descriptor, path, stat data, size, and blkid topology values, and `struct mkfs_opts`, which stores all parsed user options plus "got_*" flags. Global state is limited to `nrgrp` and `mkfs_journals`.

Important entry points and helpers:
- `opts_init`, `opts_get`, `opts_check`, `opt_parse_extended`: default and validate options.
- `test_locking`: validates `lock_dlm`, `lock_gulm`, and `lock_nolock` lock protocol/table combinations.
- `open_dev`, `probe_contents`, `choose_blocksize`: open with `O_EXCL`, use blkid probing, and choose a block size from user input or topology.
- `sbd_init`: fills `struct lgfs2_sbd`, parses/generates UUID, computes constants, validates requested filesystem and journal sizes.
- `rgs_init`, `add_rgrp`, `place_journals`, `place_rgrps`, `place_rgrp`, `zero_gap`: plan and write aligned resource groups and journal files.
- `create_jindex`, `build_per_node`: build journal index and per-node metadata.
- `main`: full mkfs transaction from option parsing to final superblock write.

Dependencies are heavy on `libgfs2` for GFS2 metadata construction, resource group planning/writing, inode creation, journal data, statfs/inum initialization, and superblock output. It also uses `libblkid` for content/topology probing, `libuuid` for UUID handling, gettext for messages, and Linux block discard ioctl support.

Behavioral flow:
1. Initialize locale/gettext and default options.
2. Parse short options and extended `-o` options including `sunit`, `swidth`, `align`, `format`, `root_inherit_jdata`, and hidden `test_topology`.
3. Validate lock table, resource group size, journal count/size, quota change size, and stripe option pairing.
4. Open target device/file exclusively, probe contents/topology unless test topology was supplied, and choose block size.
5. Warn and optionally confirm destructive formatting, then issue discard unless disabled.
6. Place journal resource groups first, then regular resource groups, tracking journal inums for `jindex`.
7. Build master directory, `jindex`, `per_node`, inum/statfs/rindex/quota/root metadata.
8. Set lock protocol/table, initialize inum/statfs state, free metadata/rgrp structures, write the superblock, `fsync`, close, and print results.

Notable edge handling:
- Regular files are accepted and use their file size; block devices use `lseek(SEEK_END)`.
- Requested filesystem size is in filesystem blocks and must fit in the target.
- User journal sizes cannot consume more than half the filesystem after multiplying by journal count.
- `-O` suppresses the confirmation prompt but does not suppress warnings.
- Debug mode prints on-disk metadata structures via `struct_print.c`.

Research notes:
- This file is the central mkfs orchestrator. Most actual on-disk structure creation is delegated to `libgfs2`.
- The file intentionally supports test-only topology injection and `UNITTESTS` exclusion of `main`.
