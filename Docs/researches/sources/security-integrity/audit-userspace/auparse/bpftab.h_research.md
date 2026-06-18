# sources/security-integrity/audit-userspace/auparse/bpftab.h

Purpose: Build-time table mapping Linux `bpf(2)` command numbers to names for auparse interpretation.

Important APIs, types, and functions: Contains `_S(number, "BPF_*")` rows for commands from `BPF_MAP_CREATE` through `BPF_PROG_BIND_MAP`. `auparse/Makefile.am` builds `bpftabs.h` with `gen_bpftabs_h --i2s bpf`.

Control flow: No runtime flow; macro-expanded by a table generator.

State and persistence: Static table source; generated header persists in the build tree.

Dependencies and integration points: Values are tied to `include/uapi/linux/bpf.h` and feed audit field interpretation for BPF command values.

Risks and edge cases: BPF command sets evolve; missing new commands will display as numeric/unknown in interpretations. Wrong values could mislead security investigations.

Test signals: Generated table build plus interpretation tests for `bpf` syscall command fields.
