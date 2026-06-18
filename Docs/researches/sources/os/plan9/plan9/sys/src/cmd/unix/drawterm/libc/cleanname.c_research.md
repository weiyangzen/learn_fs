# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/cleanname.c

This file canonicalizes Plan 9 path strings in place.

Key behavior:
- `cleanname` removes repeated slashes, `.` components, and collapses `..` where possible.
- Preserves rooted versus relative path semantics.

Important details:
- Empty results become `"."`.
- It treats `/` and NUL as path separators through `SEP`.
