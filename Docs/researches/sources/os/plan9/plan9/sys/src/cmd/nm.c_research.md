# File Research: sources/os/plan9/plan9/sys/src/cmd/nm.c

Implements Plan 9 `nm`, listing symbols from object files, archives, or executable images using `<mach.h>` object/symbol APIs.

Command flags select all symbols, globals, suppress filename headers, sort by numeric value, preserve symbol-table order, undefined-only, and type-signature output. Archive handling skips `__.SYMDEF`, iterates members with `nextar`, loads each member with `readar`, and prints member symbols under the archive/member name.

Symbol filtering is type-based: text/data/bss/local/undefined/debug records are included or suppressed according to `-a`, `-g`, and `-u`. `z` records use a filename translation table built from `m`/`f` symbols so source paths can be printed.

Output is sorted by name unless `-n` or `-s` changes behavior. Width expands from 8 to 16 hex digits when large symbol values require it.
