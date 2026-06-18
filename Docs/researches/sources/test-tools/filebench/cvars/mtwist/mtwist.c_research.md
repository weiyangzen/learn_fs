<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/mtwist/mtwist.c -->
# `sources/test-tools/filebench/cvars/mtwist/mtwist.c`

Purpose: C implementation of MT19937 Mersenne Twister PRNG with explicit-state and default-state APIs, C++ stream operators, seeding helpers, random generation, refresh logic, and state save/load.

Important APIs/functions: `mts_lrand`, `mts_llrand`, `mts_drand`, `mts_ldrand`, default wrappers `mt_lrand`, `mt_llrand`, `mt_drand`, `mt_ldrand`, seeding APIs `mts_seed32`, `mts_seed32new`, `mts_seedfull`, `mts_seed`, `mts_goodseed`, `mts_bestseed`, state APIs `mts_mark_initialized`, `mts_refresh`, `mts_savestate`, `mts_loadstate`, and default wrappers `mt_seed32`, `mt_seed32new`, `mt_seedfull`, `mt_seed`, `mt_goodseed`, `mt_bestseed`, `mt_getstate`, `mt_savestate`, `mt_loadstate`. C++ operators `operator<<` and `operator>>` serialize `mt_prng`.

Control flow: generation checks `stateptr`, refreshes when exhausted, reads reversed state entries, applies tempering macros, and returns 32-bit, 64-bit, or scaled double output. Seeding fills the 624-word state with old or new Knuth recurrence, marks initialization, and often refreshes immediately. Device seeding tries `/dev/urandom` or `/dev/random`, falls back to time, and returns the 32-bit seed. `mts_refresh` computes the MT recurrence in optimized unrolled loops and resets `stateptr`. Save/load writes/reads 624 words plus pointer.

State and persistence: `mt_state` contains 624 32-bit words, `stateptr`, and `initialized`. Global `mt_default_state` supports no-argument APIs. `mt_32_to_double` and `mt_64_to_double` are global conversion constants recalculated on initialization. Save/load persists PRNG state as text.

Dependencies and integration: includes `inttypes.h`, stdio/stdlib, time APIs, and `mtwist.h`. CVAR modules embed `mt_state` in handles and call `mts_goodseed`, `mts_mark_initialized`, and distribution helpers from `randistrs.c`.

Risks: default global state is not thread-safe. `mts_goodseed` may block on `/dev/random`; CVAR allocation uses it per handle. `mts_bestseed` reads a full state from `/dev/random` and can be very slow. Load validates only `stateptr`, not state entropy. `mts_seedfull` aborts on all-zero seed. Text state format is long and unchecked beyond scan success/pointer bounds.

Test signals: `mttest.c` and `mtcctest.cc` compare against reference vectors and exercise save/load and timing. Additional tests should cover device-fallback seeding and invalid state files.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/mtwist/mtwist.c -->
