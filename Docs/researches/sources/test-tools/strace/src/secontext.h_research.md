# sources/test-tools/strace/src/secontext.h

Purpose: public interface and compile-time stubs for SELinux context annotation support.

Important APIs/types/functions: `qualify_secontext`, `enum secontext_bits` (`SECONTEXT_FULL`, `SECONTEXT_MISMATCH`), `secontext_set`, `selinux_printfdcon`, `selinux_printfilecon`, and `selinux_printpidcon`.

Control flow: with `ENABLE_SECONTEXT`, the header declares the real functions and qualifier state; otherwise it provides no-op inline implementations for the three print hooks.

State and persistence behavior: header only; real state is the external `number_set *secontext_set` when enabled.

Dependencies and integration points: included by output and address/path decoders that want optional SELinux annotations without sprinkling compile-time guards around call sites.

Risks: no-op stubs must remain signature-compatible with real functions. Adding new secontext modes requires updating the enum, qualifier parser, and tests.

Test signals: build with and without `ENABLE_SECONTEXT`; with support enabled, verify qualifier options populate `secontext_set` and callers link to real functions.
