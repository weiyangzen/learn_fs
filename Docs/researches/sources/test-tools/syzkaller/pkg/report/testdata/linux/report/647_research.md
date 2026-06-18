# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/647

## Purpose
This is a negative/no-report fixture containing CPU vulnerability mitigation boot messages.

## Important APIs, types, and functions
There are no crash functions. The relevant strings mention Spectre V1, Spectre V2, Enhanced IBRS, RSB filling, conditional IBPB, and Speculative Store Bypass mitigation.

## Control flow
The log is early boot mitigation reporting from CPU/security initialization. It contains a line with `WARNING` in prose but no kernel warning stack.

## State and persistence behavior
The absence of metadata persists the expected parser result: no report should be produced.

## Dependencies and integration points
It tests false-positive suppression for boot-time security warning text.

## Risks and test signals
The parser must not treat `Spectre V2 : WARNING` as a crash. Correct behavior is no extracted report.
