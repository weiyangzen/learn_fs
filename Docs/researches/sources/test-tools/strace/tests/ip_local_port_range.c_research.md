<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ip_local_port_range.c -->
# sources/test-tools/strace/tests/ip_local_port_range.c

Purpose: Tests socket option decoding for Linux `IP_LOCAL_PORT_RANGE`, including the packed low/high 16-bit port range annotation.

Important APIs/types/functions: Uses `setsockopt`, `getsockopt`, `SOL_IP`, fallback definition of `IP_LOCAL_PORT_RANGE`, `socklen_t`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `TAIL_ALLOC_OBJECT_CONST_ARR`, `print_quoted_hex`, and xlat mode macros.

Control flow: Iterates thirteen packed range values. For each, it exercises negative length, zero length, short length, faulting optval, normal 4-byte optval, 5-byte length, and 8-byte oversized buffer for both setter and getter paths. The success wrapper injects `INJSTR` into every expected return line.

State/persistence behavior: The test uses fd `0` and does not create a socket in this file; expected failures or injected success keep state local. The `ports` and `big_ports` buffers are overwritten for each case.

Dependencies: Requires socket APIs, IPv4 level constants, and strace xlat macros. The option number is locally defined when absent from host headers.

Integration points: Validates strace sockopt decoders for size-sensitive integer options, packed range comments like `12345..`, raw/verbose/abbrev output, and injected-success formatting.

Risks: If run with an inherited fd 0 that is a valid IPv4 socket, return codes may differ, but decoder output is still the focus. Port-range comment formatting is easy to regress when raw mode is active.

Test signals: Many `setsockopt`/`getsockopt` lines with `[0x... /* range */]`, quoted short buffers, pointer fallback for failed getters, optional `(INJECTED)`, and clean exit.

Source read signal: complete file read for this research pass; file size 185 line(s), 5694 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ip_local_port_range.c -->
