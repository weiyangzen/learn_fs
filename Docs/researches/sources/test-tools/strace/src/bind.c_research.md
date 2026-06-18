# sources/test-tools/strace/src/bind.c

Purpose: decoder for the socket `bind` syscall.

Important APIs/types/functions: `SYS_FUNC(bind)`, `printfd`, `decode_sockaddr`, and `PRINT_VAL_D`.

Control flow: prints socket fd, decodes the sockaddr pointer using the provided `addrlen`, then prints `addrlen` as a signed integer and returns `RVAL_DECODED`.

State and persistence behavior: no persistent state; reads tracee memory for sockaddr decoding.

Dependencies and integration points: integrates with generic socket address decoders and syscall table entries for networking syscalls.

Risks: invalid or short `addrlen` affects `decode_sockaddr` output. Address family-specific decoding depends on other modules.

Test signals: bind tests for IPv4, IPv6, Unix-domain, netlink, invalid pointers, and short lengths should verify formatting.
