# sources/test-tools/strace/src/socketcall.c

Purpose: decodes the legacy multiplexed `socketcall` syscall shell.

Important APIs/types/functions: `SYS_FUNC(socketcall)` and `socketcalls` xlat table.

Control flow: prints the socket subcall number symbolically and prints the argument vector address without decoding the nested arguments here.

State and persistence behavior: stateless.

Dependencies and integration points: used on architectures with legacy socketcall multiplexing; detailed subcall decoding is handled elsewhere after syscall dispatch.

Risks: intentionally shallow; if syscall dispatch does not remap subcalls, output remains only the raw argument vector.

Test signals: known and unknown socketcall numbers and argument pointer formatting.
