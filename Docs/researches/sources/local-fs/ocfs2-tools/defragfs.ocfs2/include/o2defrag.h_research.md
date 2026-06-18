# File Research: sources/local-fs/ocfs2-tools/defragfs.ocfs2/include/o2defrag.h

## Role

`o2defrag.h` defines constants, option flags, and ioctl fallback definitions for `defragfs.ocfs2`.

## Contents

It defines the OCFS2 filesystem type string, mode flags for detail/statistic/resume/low-I/O behavior, file target kind constants, open file descriptor count for `nftw`, root UID, output scheduling constants, record interval, program name, and the fallback `OCFS2_IOC_MOVE_EXT` ioctl number.

## Data Types

`struct o2defrag_opt` maps a mode bit to its option string, and `declare_opt()` initializes table entries.
