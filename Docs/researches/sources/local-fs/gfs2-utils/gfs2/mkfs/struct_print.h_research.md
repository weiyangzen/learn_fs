# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/struct_print.h

Header declaring the GFS2 on-disk debug printer functions.

Exports printers for inum, meta header, superblock, dinode, log header/descriptor, quota, quota change, statfs change, leaf, rindex, and rgrp.

Research notes:
- Comment states the functions expect on-disk data, meaning callers must not pass already CPU-endian transformed copies unless they want misleading output.
