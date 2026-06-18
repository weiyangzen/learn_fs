<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-success-long-y.c -->
## sources/test-tools/strace/tests/bpf-success-long-y.c

Purpose: Injected-success BPF decoder variant with fd path decoding enabled and `/dev/full` expected for fd 0.

Important APIs/types/functions: Defines `INJECT_RETVAL ((long) 0xbadc0de1e55beefULL)`, `FD0_PATH "</dev/full>"`, `YFLAG`, and includes `bpf.c`.

Control flow: Runs the full `bpf.c` table-driven decoder under injected return behavior, while `YFLAG` makes `AT_FDCWD` print with resolved path and `FD0_PATH` changes fd-zero annotations.

State and persistence: Inherits `bpf.c` tail allocations and syscall probes; no real successful BPF side effects because results are injection-oriented.

Dependencies and integration: Used as a decoder/injection test for long return values and `-y` path output.

Risks: Expected output tightly couples injected return text, fd path setup, and architecture word-size formatting.

Test signals: Lines should show injected BPF return value, fd zero rendered as `</dev/full>`, and `AT_FDCWD<...>` where applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/bpf-success-long-y.c -->
