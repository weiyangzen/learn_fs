<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ip_protocol.c -->
# sources/test-tools/strace/tests/ip_protocol.c

Purpose: Tests `getsockopt` decoding for Linux `IP_PROTOCOL`, including known and unknown protocol numbers under injected-success formatting.

Important APIs/types/functions: Uses `getsockopt`, `SOL_IP`, fallback `IP_PROTOCOL`, `socklen_t`, tail-allocated integer buffers, `print_quoted_hex`, and xlat macros.

Control flow: Iterates `IPPROTO_RAW` and an unknown protocol value. For each it tests negative, zero, short, faulting, normal, 5-byte, and 8-byte option lengths, printing either pointer fallback or decoded `[IPPROTO_*]` output.

State/persistence behavior: No socket is created here; fd `0` is used and the file hardcodes `(INJECTED)` in expected output. State is limited to `protocol`, `big_protocol`, and `len`.

Dependencies: Requires socket headers and the strace sockopt decoder. The option number is defined locally when missing.

Integration points: Covers get-only socket option decoding, xlat verbosity behavior for protocol constants, short-buffer hex rendering, and injected-success expected output.

Risks: Without injection the real fd type may influence return codes; the test suite normally controls this through strace fault injection.

Test signals: Lines should show `IPPROTO_RAW`, `IPPROTO_???`, quoted short buffers, `(INJECTED)`, and clean exit.

Source read signal: complete file read for this research pass; file size 109 line(s), 2932 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ip_protocol.c -->
