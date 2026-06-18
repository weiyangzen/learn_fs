# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/wcsxfrm.c

Read completely: 71 lines.

This file implements `wcsxfrm` and `wcsxfrm_l` as a simple copy/length transform. It returns `wcslen(s2)` and copies `s2` to `s1` only if it fits within `n`.

Important interactions: locale argument is ignored because `LC_COLLATE` is not implemented.

Security/reliability notes: if the transformed length is `n` or more, it leaves the destination unspecified by doing nothing, matching the cited SUSv3 behavior. No locale collation transform is performed.
