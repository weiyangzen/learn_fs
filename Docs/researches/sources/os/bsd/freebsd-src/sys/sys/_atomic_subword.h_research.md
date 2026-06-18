# File Research: sources/os/bsd/freebsd-src/sys/sys/_atomic_subword.h

Fallback implementation for 8-bit and 16-bit atomic operations on platforms that only support word-sized atomics.

Defines:
- Word alignment and endian-dependent shift macros for byte/halfword positions.
- `_atomic_cmpset_masked_word()` and `_atomic_fcmpset_masked_word()` to update subword fields inside a 32-bit word using masks.
- Fallback `atomic_cmpset_8`, `atomic_fcmpset_8`, `atomic_cmpset_16`, `atomic_fcmpset_16`.
- Fallback `atomic_load_acq_8`, `atomic_load_acq_16`.
- Fallback looping `atomic_set_16` and `atomic_clear_16`.

Important behavior:
- Compare-and-set loops distinguish failures caused by the target subword from unrelated changes in the same aligned word.
- `fcmpset` intentionally permits one-shot/spurious failure behavior consistent with `atomic(9)`.
- Direct inclusion is blocked; it must come from `machine/atomic.h`.

Research relevance:
- Shows how FreeBSD keeps fine-grained atomic APIs portable even when hardware lacks byte/halfword atomic instructions.
