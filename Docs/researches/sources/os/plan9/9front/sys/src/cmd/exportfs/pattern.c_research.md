# File Research: sources/os/plan9/9front/sys/src/cmd/exportfs/pattern.c

This file implements exportfs include/exclude pattern filtering and filtered directory reads.

Key responsibilities:
- Reads a pattern file where lines beginning `+ ` define required include regexps and lines beginning `- ` define exclude regexps.
- Compiles patterns with Plan 9 regex.
- Applies include and exclude logic in `excludefile`.
- Implements `preaddir`, a directory reader that filters entries while maintaining 9P directory offsets.

Important implementation notes:
- Include patterns are all required: if any include regexp does not match, the path is excluded.
- Exclude patterns reject a path when any regexp matches.
- Paths are normalized by dropping the leading `.` path prefix, with root represented as `/`.
- `preaddir` cannot seek arbitrary directory offsets except reset to 0 or continue from current filtered offset.
