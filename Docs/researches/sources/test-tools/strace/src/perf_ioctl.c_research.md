<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/perf_ioctl.c -->
# sources/test-tools/strace/src/perf_ioctl.c

Purpose: decodes perf event ioctl commands.

Important APIs/types/functions: `perf_ioctl`, `perf_ioctl_query_bpf`, `perf_ioctl_modify_attributes`, `PERF_EVENT_IOC_*`, and `perf_ioctl_flags`.

Control flow: simple commands print flags, counts, fds, strings, ids, or numeric args. `QUERY_BPF` prints `ids_len` on entry and `prog_cnt` plus `ids` on exit. `MODIFY_ATTRIBUTES` reuses `fetch_perf_event_attr` and `print_perf_event_attr`.

State and persistence behavior: uses syscall phase and may rely on perf attr tcb private data through shared perf helpers.

Dependencies and integration points: personality-aware `MPERS_PRINTER_DECL` ioctl decoder; depends on `<linux/ioctl.h>`, `perf_event_struct.h`, and perf syscall attr helpers.

Risks: pointer-size-sensitive ioctls need mpers handling. Query BPF output count controls array length, so failed exits must preserve a syntactically closed partial struct.

Test signals: enable/disable/reset flags, refresh, period, set-output fd, set-filter string, id output, query-bpf success/error, and modify-attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/perf_ioctl.c -->
