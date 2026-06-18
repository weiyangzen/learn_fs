<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/number_set.h -->
# sources/test-tools/strace/src/number_set.h

Purpose: public declarations for qualifier number sets and related option enums.

Important APIs/types/functions: opaque `struct number_set`, membership/allocation functions, `enum status_t`, `enum quiet_bits`, `enum decode_fd_bits`, `enum decode_pid_bits`, and extern global sets such as `trace_set`, `signal_set`, `quiet_set`, `decode_fd_set`, and `inject_set`.

Control flow: no runtime flow; API declarations only.

State and persistence behavior: declares process-wide mutable qualifier state owned by other translation units.

Dependencies and integration points: included by path tracing, open fd formatting, injection, filters, and PID namespace translation.

Risks: enum ordering is part of option parsing and membership checks; changes require updating parsers and tests. Globals make initialization order important.

Test signals: qualifier parsing tests for quiet/decode-fd/decode-pid bits, syscall filter membership, and build coverage for all extern sets.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/number_set.h -->
