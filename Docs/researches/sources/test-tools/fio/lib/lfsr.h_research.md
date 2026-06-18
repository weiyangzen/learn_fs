# sources/test-tools/fio/lib/lfsr.h

Purpose: declares LFSR state and public sequence functions.

Important APIs/types: `FIO_MAX_TAPS`, `struct lfsr_taps`, `struct fio_lfsr`, `lfsr_init`, `lfsr_reset`, and `lfsr_next`.

Control flow/state: callers allocate the state struct, initialize with size/seed/spin, then repeatedly call `lfsr_next` until it returns nonzero. `lfsr_reset` restarts with a new seed while preserving configuration.

Dependencies/integration: fixed-width integer types only. The state struct is designed for embedding inside fio job/random state.

Risks/test signals: callers must check initialization and reset failures for unsupported sizes or illegal seeds. Tests should cover exhaustion and repeatability.
