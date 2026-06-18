# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse_lowlevel.c

This file implements command-line parsing support and help/version stubs for the low-level API. It defines option templates for help, version, debug, foreground, singlethread, and `fsname`, prints ReFUSE option help, parses a single mountpoint as a non-option, and adds a default `fsname=refuse:<program>` if none was provided.

`__fuse_parse_cmdline` always sets `singlethread = 1` because puffs does not currently support multithreaded operation. `fuse_lowlevel_version` is a placeholder that prints nothing.

Risks: command-line behavior is intentionally partial compared with libfuse, `-s` cannot be disabled in practice, and version output is unimplemented.
