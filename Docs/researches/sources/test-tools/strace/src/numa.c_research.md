<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/numa.c -->
# sources/test-tools/strace/src/numa.c

Purpose: decodes NUMA policy and page migration syscalls.

Important APIs/types/functions: `print_nodemask`, `print_mode`, `SYS_FUNC(migrate_pages)`, `mbind`, `set_mempolicy`, `get_mempolicy`, `set_mempolicy_home_node`, and `move_pages`.

Control flow: nodemasks are printed as word arrays sized from `maxnode` and current word size. Policy modes are split into base `MPOL_*` and `MPOL_F_*` flags. Enter/exit phases differ for `get_mempolicy` and `move_pages` because output buffers and status arrays are only meaningful on exit.

State and persistence behavior: no persistent state.

Dependencies and integration points: depends on xlat tables for NUMA policy modes/flags and move flags, pid translation, array printers, and tracee memory fetch.

Risks: nodemask size arithmetic guards overflow but large user values can still be abbreviated by generic array truncation. Mode/flag split must track kernel additions.

Test signals: migration nodemask arrays, mbind flag combinations, get_mempolicy output mode/nodemask, move_pages page and status arrays, invalid pointers, and large `maxnode` edge cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/numa.c -->
