# File Research: sources/local-fs/ocfs2-tools/o2info/o2info.h

This header defines the `o2info` CLI framework: target access method enum, `struct o2info_method` union for either `ocfs2_filesys *` or fd, operation descriptors, option descriptors, and task list nodes.

The `DEFINE_O2INFO_OP` macro creates global `struct o2info_operation` objects used by `operations.c` and referenced by `o2info.c`. This keeps operation metadata and run callbacks decoupled from command-line parsing.

It depends on `getopt.h`, `libocfs2`, and the kernel list implementation for the operation task list.
