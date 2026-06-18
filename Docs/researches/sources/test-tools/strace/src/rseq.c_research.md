# sources/test-tools/strace/src/rseq.c

Purpose: Decodes the `rseq` syscall and `struct rseq` registration fields.

Important APIs/types/functions: `SYS_FUNC(rseq)` plus helpers for CPU-id, flags, signature, and structure-size rendering.

Control flow: prints the user rseq pointer, length, flags, and signature; when appropriate it fetches and decodes the pointed structure with field-level output.

State and persistence: stateless with respect to strace; kernel registration state belongs to the tracee.

Dependencies/integration: Linux rseq UAPI definitions, xlat tables for rseq flags, and tracee memory fetch helpers.

Risks: rseq is ABI-size-sensitive; future struct extensions and user-specified length must be handled without over-reading. Signature is architecture-specific.

Test signals: `rseq` register/unregister calls, different lengths, invalid pointers, unknown flags, and raw/verbose xlat modes.
