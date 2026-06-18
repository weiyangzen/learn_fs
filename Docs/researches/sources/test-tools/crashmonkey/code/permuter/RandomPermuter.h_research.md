# sources/test-tools/crashmonkey/code/permuter/RandomPermuter.h

Purpose: declares the deterministic random permuter plugin.

Important APIs/types: `GenRandom` is an adapter used by `random_shuffle`. `RandomPermuter` extends `Permuter`, providing constructors and overrides for whole-bio and sector crash-state generation.

Control flow and integration: `RandomPermuter.so` is the default permuter loaded by `c_harness.cpp`; factory symbols in the `.cpp` instantiate it for the harness.

State: stores one mt19937 for selecting crash points and one `GenRandom` for subset shuffling.

Dependencies: includes `Permuter.h`, `utils.h`, and `PermuteTestResult.h`.

Risks and test signals: stateful RNG means generation is order-dependent; fixed seeds make results reproducible. Header exposes no method to set a seed, so tests needing different exploration must change code or load another plugin.
