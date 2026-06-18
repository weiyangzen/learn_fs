# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/27

Purpose: Companion OpenBSD socket receive fixture for an alphanumeric receive invariant. Expected title is `soreceive 1a`.

Important parser APIs and patterns: uses the same `panic: receive ([0-9][a-z]*):` title rule as report/26. Because the captured token is `1a`, generic numeric replacement should not reduce it to `NUM`.

Control flow: the kernel panics in `soreceive` while `dhclient` reads from a socket. The stack is `soreceive`, `soo_read`, `dofilereadv`, `sys_read`, `syscall`, `Xsyscall`, followed by repeated DDB `show panic` and `trace`, registers, and pool statistics.

State and persistence: static fixture preserving socket pointer, socket type, mbuf pointer, and mbuf type. These values are noisy kernel state; only the receive checkpoint token is title-relevant.

Dependencies and integration: validates subtle title sanitization behavior in the OpenBSD reporter and shared report package. It proves alphanumeric invariants can remain distinct from purely numeric ones.

Risks: overly aggressive dynamic-title replacement could collapse `1a` into `NUM`, merging different socket receive invariants. Report-boundary logic must tolerate long trailing diagnostics.

Test signals: exact title `soreceive 1a`; stack includes `soreceive+0x170a`.
