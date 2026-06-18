<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mpers.awk -->
# sources/test-tools/strace/src/mpers.awk

Purpose: generates mpers-compatible C type definitions from normalized DWARF debug information.
Important APIs/types/functions: awk functions `array_get`, `norm_idx`, `array_seq`, `enter/leave`, `update_upper_bound`, `what_is`, global arrays for DIE attributes, and `ARCH_FLAG`/`VAR_NAME` inputs.
Control flow: BEGIN derives pointer size and prints stdint include; parsing rules collect DIE indexes, names, sizes, encodings, types, locations, array bounds, and parent relationships; END emits `mpers_ptr_t` and a packed typedef for the requested variable type.
State and persistence behavior: all state is in awk arrays during one run. Dependencies and integration points: invoked by `mpers.sh` after `readelf` preprocessing.
Risks: DWARF format assumptions, recursive type loops, padding math, and gawk-specific `asorti` affect generated ABI structs. Test signals: `mpers_test.sh` expected-output comparison and multi-arch mpers builds.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mpers.awk -->
