# File Research: sources/os/bsd/netbsd-src/lib/libc/resolv/res_debug.h

Read completely: 37 lines.

This header defines resolver debug macros. Without `DEBUG`, `Dprint`, `DprintQ`, `Aerror`, and `Perror` compile away. With `DEBUG`, `Dprint` emits `fprintf`, and `DprintQ` emits text plus `res_pquery(statp, query, size, stdout)`.

Important interactions: included by `res_send.c` to gate transport diagnostics and packet dumps.

Security/reliability notes: the macros assume a visible `statp` variable for `DprintQ`; this is an old-style local-context macro contract.
