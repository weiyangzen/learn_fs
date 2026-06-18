# File Research: sources/os/bsd/freebsd-src/sys/sys/_smr.h

Safe Memory Reclamation core typedefs and assertions.

Key elements:
- Defines `smr_seq_t`, `smr_delta_t`, and opaque `smr_t`.
- Provides `SMR_ENTERED`, `SMR_ASSERT_ENTERED`, `SMR_ASSERT_NOT_ENTERED`, and `SMR_ASSERT`.

Dependencies:
- Assumes kernel globals/helpers such as `curthread`, `zpcpu_get`, `SMR_SEQ_INVALID`, and `KASSERT`.

Research notes:
- SMR is a lockless read-side reclamation scheme for high-concurrency kernel structures.
- Assertions verify critical-section state.
