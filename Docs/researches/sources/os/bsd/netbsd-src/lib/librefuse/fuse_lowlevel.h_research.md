# File Research: sources/os/bsd/netbsd-src/lib/librefuse/fuse_lowlevel.h

This public header supplies a small subset of the FUSE low-level header surface, mainly `struct fuse_cmdline_opts`, `fuse_lowlevel_version`, and `fuse_cmdline_help`. The struct has explicit reserved space and a comment warning that size/layout changes break ABI compatibility.

Integration points: parsed and filled by `refuse_lowlevel.c` and used by setup wrappers in `refuse.c` and version adapters. Main risk is ABI drift from upstream FUSE command-line option structures.
