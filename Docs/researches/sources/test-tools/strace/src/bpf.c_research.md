<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/bpf.c -->
## sources/test-tools/strace/src/bpf.c

Purpose: Implements the `bpf(2)` syscall decoder. It translates `cmd`, the user-supplied `union bpf_attr` byte buffer, and size-specific command layouts into structured strace output, including newer kernel fields while tolerating older shorter `attr` sizes.

Important APIs and types: The core abstraction is the `BEGIN_BPF_CMD_DECODER`/`END_BPF_CMD_DECODER` macro pair, which copies up to the known command-specific struct size from the syscall buffer, then lets a decoder print fields conditionally by `len`. `SYS_FUNC(bpf)` dispatches through `bpf_cmd_decoders[]`. Helper types include local `struct ebpf_insn`, `struct ebpf_insns_data`, `struct obj_get_info_saved`, `print_bpf_obj_info_fn`, and `union strace_bpf_iter_link_info`.

Control flow: On entry, `SYS_FUNC(bpf)` prints `cmd` and `attr`, validates `size <= get_pagesize()`, fetches the attr into a static page-sized buffer, and invokes the command decoder. The command decoders cover map creation and element operations, program load, object pin/get, attach/detach, test run, id iteration, object info, prog query, raw tracepoint, BTF load/get, task fd query, batch map operations, link create/update/detach, iterator create, token create, program stream read, and struct-ops association. Several decoders intentionally return `0` on entry so exit-time output fields can be printed after the kernel writes them.

State and persistence: Uses `set_tcb_priv_ulong` for counts (`BPF_PROG_QUERY`, batch operations, task fd query) and `set_tcb_priv_data` for `BPF_OBJ_GET_INFO_BY_FD` entry snapshots. `print_boottime` caches the realtime-to-boottime offset in a static `timespec`. Static buffers are allocated once for syscall attr and BPF object info.

Dependencies and integration: Depends on `defs.h`, `bpf_attr.h`, `<linux/bpf.h>`, `<linux/filter.h>`, xlat tables for BPF commands/types/flags, and the generic print/fetch APIs. It integrates with `bpf_filter.c` via `print_bpf_filter_code` for eBPF instruction code decoding.

Risks: Layout drift is the dominant risk; the decoder manually mirrors many kernel UAPI versions and union interpretations. Incorrect `offsetof` gates can mislabel fields for old kernels. Static buffers are page-sized, so oversized attrs deliberately fall back to address printing. Link-create union decoding is partly inferred from `attach_type`, and TODO comments note ambiguous cases.

Test signals: Exercise `bpf` command families with varying attr sizes, including output fields that change across entry/exit. Regression tests should cover `BPF_PROG_LOAD` instruction/log printing, `BPF_OBJ_GET_INFO_BY_FD` map/program object detection, link-create attach types, batch count mutation, and unknown or oversized attr fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/bpf.c -->
