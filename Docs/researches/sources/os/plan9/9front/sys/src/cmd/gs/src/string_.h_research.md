# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/string_.h

Generic substitute for Unix `string.h`.

Key points:
- Includes `std.h` before system headers.
- Uses `<strings.h>` and maps `strchr` to `index` for `BSD4_2`.
- Otherwise includes `<string.h>`.
- Supports `MEMORY__NEED_MEMMOVE` by mapping `memmove` to `gs_memmove`.
- Patches Think C `strlen` return handling.

Dependencies and interactions:
- Used by code needing string/memory functions while respecting Ghostscript header ordering rules.

Research relevance:
- Small portability wrapper around system string APIs and Ghostscript’s fallback `memmove`.
