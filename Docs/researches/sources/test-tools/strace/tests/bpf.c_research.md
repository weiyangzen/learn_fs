<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/bpf.c -->
## sources/test-tools/strace/tests/bpf.c

Purpose: Large table-driven decoder test for the `bpf` syscall across map, program, object, query, link, BTF, batch, token, stream-read, and struct-ops commands.

Important APIs/types/functions: Defines `union bpf_attr_data`, `struct bpf_attr_check`, `struct bpf_check`, `sys_bpf`, `print_bpf_attr`, `test_bpf`, many `BPF_*_checks` arrays, command-specific init/print callbacks, `attach_type_is_ifindex`, `skip_special_attach_types`, `CHK`, and `main`. Uses `bpf_attr.h`, `print_fields.h`, `xmalloc.h`, BPF xlat tables, `tail_alloc`, `tail_memdup`, `fill_memory_ex`, and optional macros `VERBOSE`, `INJECT_RETVAL`, `YFLAG`, and `FD0_PATH`.

Control flow: `main` computes page-boundary buffers and `AT_FDCWD` text, then iterates a `checks[]` table for each BPF command. `test_bpf` probes NULL attrs, zero size, each declared attr size, short reads, exact union-size reads, non-zero trailing data, page-sized reads, and over-page sizes. Command tables cover evolving UAPI fields including map create BTF/token/hash fields, prog load signature/core relo/fd arrays, object pin/get path fd flags, attach/detach/query flags, raw tracepoints, BTF load, task fd query, batch ops, link create variants for cgroup/perf/kprobe/uprobe/netfilter/tcx/netkit/tracing, link update/detach, enable stats, iter create, prog bind map, token create, prog stream read, and prog assoc struct ops.

State and persistence: Uses process memory at page boundaries to test decoder fault handling and allocates tail buffers for strings/arrays. Real BPF syscalls usually fail because attrs are synthetic; injected variants override returns. No persistent kernel objects are expected from the invalid probes.

Dependencies and integration: This is a central regression test for `src/bpf.c` and related printers/xlat tables. Wrapper files enable verbose output, injected success, long return values, fd path decoding, and fd-zero path annotations.

Risks: Very sensitive to Linux BPF UAPI growth: static assertions on map/prog xlat array sizes intentionally force test updates when tables change. Architecture pointer width and endianness affect expected address rendering. The volume of generated output makes small format changes high blast radius.

Test signals: Passing tests show stable decoding for all command tables, unknown command fallback, short/bad pointer handling, extra_data behavior, flag/xlat expansion, wrapper-specific verbose/injected/path modes, and final clean exit.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/bpf.c -->
