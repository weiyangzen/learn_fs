# sources/test-tools/fio/lib/lfsr.c

Purpose: implements a maximal-length linear feedback shift register generator for deterministic non-repeating random-like sequences over a bounded range.

Important APIs/functions: `lfsr_init`, `lfsr_reset`, and `lfsr_next`. Static tap tables define primitive polynomials for 3-63 bits; helpers create XOR masks, choose a tap width for the requested size, and prepare "spin" behavior.

Control flow: initialization chooses taps whose period exceeds the requested range, builds masks, validates spin <= 15, and seeds the state. `lfsr_next` advances the register by `spin` steps, handles precomputed spin sub-cycles, rejects values above `max_val`, and stops after all values have been produced.

State/persistence: all mutable sequence state lives in `struct fio_lfsr`: last value, generated count, max value, XOR mask, cached top bit, spin, and cycle counters. No heap allocation.

Dependencies/integration: includes `compiler.h` for fallthrough annotations. Used by fio random map modes that require repeatable coverage without replacement.

Risks/test signals: all-ones seed is illegal for the XNOR form; sizes needing >=64-bit taps fail. Spin cycle math is subtle and should be tested for repeat-free coverage. Signals include deterministic sequences, no out-of-range values, and correct exhaustion.
