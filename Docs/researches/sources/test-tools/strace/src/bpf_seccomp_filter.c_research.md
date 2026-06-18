<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/bpf_seccomp_filter.c -->
## sources/test-tools/strace/src/bpf_seccomp_filter.c

Purpose: Specializes BPF program printing for seccomp filters by decoding `BPF_RET` constants as seccomp return actions.

Important APIs and types: Static `print_seccomp_filter_k` callback, exported `print_seccomp_fprog`, and exported `decode_seccomp_fprog`.

Control flow: The callback checks whether an instruction class is `BPF_RET`. It splits `k` into `SECCOMP_RET_ACTION_FULL` action and data payload, prints the symbolic action from `seccomp_ret_action`, and appends non-zero data bits. Non-return instructions fall back to generic hex `k` printing in `bpf_filter.c`.

State and persistence: No persistent state.

Dependencies and integration: Depends on `bpf_filter.h`, `<linux/filter.h>`, `<linux/seccomp.h>`, and `xlat/seccomp_ret_action.h`. Used by seccomp-related syscall decoders to display loaded filters.

Risks: Only `BPF_RET` gets semantic treatment; malformed or non-standard filters are still printed structurally but may not convey policy intent.

Test signals: Seccomp filter tests should include allow, errno, trap, trace, kill, user-notif actions, action data payloads, and non-return BPF statements.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/bpf_seccomp_filter.c -->
