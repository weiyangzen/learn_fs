<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/lookup_test.c -->
# sources/security-integrity/audit-userspace/auparse/test/lookup_test.c

Purpose: generated-table integrity test for auparse integer-to-string interpretation tables.

Important APIs and functions: the `TEST_I2S` macro checks every `_S(value,string)` entry from each table header against the corresponding `*_i2s` function, then probes 1000 random absent values for `NULL`. Test functions cover capability, clock, epoll, address family, fcntl, fsconfig, ICMP, netfilter hooks/actions/protocols, ioctl, socket, personality, prctl, ptrace, resource limit, scheduler, seccomp, signal, and normalization maps.

Control flow and state: `main` seeds `rand()` with a fixed value, runs all table-specific functions, and prints a pass banner. The headers are included twice per table family: one include creates the test array and another exposes the lookup function.

Dependencies and integration: depends on `gen_tables.h`, many auparse generated headers, and selected system headers for constants. `run_auparse_tests.sh.in` invokes it after parser golden-file checks.

Risks and test signals: high coverage for table drift and missing generated entries, but it only verifies `i2s`, not string-to-int or flag-composition helpers. Random negative checks are deterministic but collision-prone if future constants equal the sampled values.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/test/lookup_test.c -->
