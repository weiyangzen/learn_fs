# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse_compat.c

This file preserves old unversioned librefuse ABI symbols. It defines a previous `struct fuse_cmdline_opts_rev0` and compatibility implementations for old `fuse_daemonize`, `fuse_main_real`, `fuse_mount`, `fuse_new`, `fuse_destroy`, `fuse_parse_cmdline`, `fuse_unmount`, and `fuse_unmount_compat22`.

Most symbols use `__warn_references` so linkers can warn callers that they are binding to compatibility symbols. The implementations delegate to modern versioned APIs, often FUSE 3.0 or 2.6 paths.

Risks: this intentionally preserves ABI but not always source API compatibility, especially the old incorrect `fuse_daemonize` prototype and old command-line option struct size.
