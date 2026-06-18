# File Research: sources/windows/winfsp/src/dll/fuse/fuse_opt.c

This file implements libfuse-compatible option parsing and argument manipulation.

Key responsibilities:
- Matches option templates against command-line arguments, including exact matches, value-in-same-arg matches, and value-in-next-arg matches.
- Supports `%` conversion specs for integer and string options, with platform-specific handling for `long` width on Cygwin64 vs Win64.
- Parses `-o` comma-separated option lists, including escaped comma/backslash support.
- Calls user option processors with FUSE keys such as `FUSE_OPT_KEY_KEEP`, `FUSE_OPT_KEY_DISCARD`, `FUSE_OPT_KEY_OPT`, and `FUSE_OPT_KEY_NONOPT`.
- Preserves unknown/kept options into output args, grouping `-o` options as expected by FUSE.
- Provides public helpers:
  - `fsp_fuse_opt_parse`
  - `fsp_fuse_opt_add_arg`
  - `fsp_fuse_opt_insert_arg`
  - `fsp_fuse_opt_free_args`
  - `fsp_fuse_opt_add_opt`
  - `fsp_fuse_opt_add_opt_escaped`
  - `fsp_fuse_opt_match`

Filesystem relevance:
- This enables Unix/FUSE-style mount option parsing in the Windows DLL environment.
- It is foundational for `fuse_main.c`, core option parsing, and FUSE3 compatibility setup.
