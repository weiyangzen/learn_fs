# sources/test-tools/strace/tests/net-tpacket_stats-success.c

Purpose: creates an injected-success variant of `net-tpacket_stats.c` by defining `INJECT_RETVAL 42` before including the shared source. It checks the same decoder paths when strace syscall injection makes `getsockopt` appear successful.

Important APIs, types, and helpers: inherits all code from `net-tpacket_stats.c`, particularly `getsockopt`, `PACKET_STATISTICS`, `struct tp_stats`, and `sprintrc`; adds the `INJECT_RETVAL` compile-time control.

Control flow: there is no local function body. The included file compiles with an extra return-value assertion and appends `(INJECTED)` to expected return text when the injected return value matches.

State and persistence: no local state. The included code uses stack/tail-allocated optlen and stats buffers; this wrapper only changes compile-time behavior.

Dependencies and integration points: integrated through the strace test suite’s injection machinery. The source must be built in a test configuration where syscall injection causes the expected synthetic return value.

Risks and edge cases: if the included implementation changes the injection contract or the expected return value, this thin wrapper will fail. It also shares all optlen boundary risks from the base file.

Test signals: output mirrors `net-tpacket_stats.c` but successful calls should include injected return formatting and the program must fail early if the observed return differs from `42`.
