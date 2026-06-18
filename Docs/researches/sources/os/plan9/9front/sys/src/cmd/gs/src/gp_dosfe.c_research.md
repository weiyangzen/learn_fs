# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_dosfe.c

MS-DOS file enumeration implementation.

Key behavior:
- Defines `file_enum_s` with DOS find state, original and translated patterns, directory-prefix size, and allocator.
- Translates Ghostscript wildcard patterns into DOS-compatible patterns, including converting bare `*` to `*.*`.
- Uses `dos_findfirst` and `dos_findnext` to enumerate directory entries.
- Reattaches the original directory prefix and strips spaces from DOS file names.
- Uses Ghostscript `string_match` as a post-filter to enforce the original pattern.

Notable dependencies:
- DOS compatibility wrappers from `dos_.h`.
- Ghostscript GC descriptors and `gsutil.h` string matching.

Research notes:
- The comment notes DOS limitations with wildcards in directory components and backslash escaping.
