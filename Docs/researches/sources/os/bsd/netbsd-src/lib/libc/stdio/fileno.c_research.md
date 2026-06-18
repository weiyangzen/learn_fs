# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fileno.c

Read completely: 70 lines.

This file implements `_fileno` and weak aliases `fileno` to it. It locks the stream, returns `__sfileno(fp)`, and unlocks.

Important interactions: public function form of the descriptor macro.

Security/reliability notes: descriptor validity behavior is delegated to `__sfileno`.
