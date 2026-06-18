## sources/test-tools/filebench/cvars/mtwist/mtwist.h

### Purpose
`mtwist.h` is the C and C++ public interface for the bundled Mersenne Twister pseudo-random number generator. It defines the generator state object, the seeding/state-persistence API, the default-generator API, conversion helpers, tempering macros, and the C++ `mt_prng` wrapper. Filebench uses this PRNG indirectly through `fb_random.c`, while the mtwist distribution library uses the state-based functions to build higher-level distributions.

### Important APIs, Types, And Functions
The central type is `mt_state`, containing `statevec[MT_STATE_SIZE]`, `stateptr`, and an `initialized` flag. `MT_STATE_SIZE` is fixed at 624, matching the 32-bit MT19937 state. State-specific APIs include `mts_seed32`, `mts_seed32new`, `mts_seedfull`, `mts_seed`, `mts_goodseed`, `mts_bestseed`, `mts_refresh`, `mts_savestate`, and `mts_loadstate`. Default-generator APIs mirror those without the `mts_` state parameter: `mt_seed32`, `mt_goodseed`, `mt_bestseed`, `mt_getstate`, `mt_savestate`, and `mt_loadstate`. Generation APIs include `mts_lrand`, `mts_llrand`, `mts_drand`, `mts_ldrand`, plus default-state versions `mt_lrand`, `mt_llrand`, `mt_drand`, and `mt_ldrand`. The C++ class `mt_prng` wraps a protected `mt_state` and exposes constructors, seed methods, random-value methods, stream operators, and `operator()`.

### Control Flow
This header is mostly declarations, but it also fixes the interface contract used by the implementation in `mtwist.c`: callers seed an `mt_state`, then draw 32-bit, 64-bit, or floating-point values. The comments document the reversed state-vector traversal, where zeroed state is treated as uninitialized and refreshes are triggered by a zero-oriented pointer test. The tempering macros apply the MT19937 bit-mixing steps to generated state words.

### State And Persistence
State is explicit through `mt_state` or implicit through exported `mt_default_state`. The save/load functions persist generator state in ASCII to a `FILE *`, allowing deterministic replay. Seeding can derive entropy from `/dev/urandom`, `/dev/random`, or time fallback depending on the API. `mt_32_to_double` and `mt_64_to_double` are exported conversion multipliers shared by random-distribution code.

### Dependencies And Integration Points
The header depends on `stdio.h`, `stdint.h`, and C++ `iostream` when compiled as C++. `randistrs.h` includes this header and uses the protected C++ `mt_prng::state` through friendship for empirical distributions. Filebench includes `cvars/mtwist/mtwist.h` from `fb_random.c` to use `mt_llrand()` as a default random source.

### Risks
The implementation assumes a 32-bit PRNG word; changing integer widths or constants would break distribution quality. The default generator is global state and not inherently synchronized. The seed APIs provide only 32 bits of entropy for `seed`/`goodseed`, which is adequate for benchmarking reproducibility but not cryptographic use. The header advertises `mt_default_state` as an undocumented external, which makes coupling convenient but exposes internals.

### Test Signals
Relevant tests are the mtwist test programs elsewhere in the directory and the distribution harnesses `rdtest.c` and `rdcctest.cc`. Practical verification should check deterministic sequences for fixed seeds, save/load round trips, zero-initialized state behavior, 32-bit/64-bit generation paths, and C++ wrapper parity with the C state APIs.
