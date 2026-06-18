# sources/test-tools/crashmonkey/code/permuter/RandomPermuter.cpp

Purpose: implements a deterministic pseudo-random permuter plugin that chooses a crash point and drops a random subset of bios or sectors from the final epoch.

Important APIs/functions: `GenRandom` wraps a fixed-seed mt19937 for `random_shuffle`. `RandomPermuter::gen_one_state()` chooses a number of epochs and operations, copies complete prior epochs, and subsets the final epoch. `gen_one_sector_state()` chooses a crash epoch, optionally coalesces sectors in the final epoch, drops a subset, and emits `DiskWriteData`. `subset_epoch()` selects bios from an epoch while preserving order. `AddEpochs()` copies full epochs into replay output. The `extern "C"` factory/defactory expose the plugin to `ClassLoader`.

Control flow: whole-bio generation picks `num_epochs` in `[1, epochs.size()]`, then picks a prefix length in the last epoch. Sector generation similarly picks a final epoch and request prefix, expands it into sectors, handles full barrier epochs as non-reorderable, coalesces duplicate sector offsets, and selects sectors by bitmap so temporal order is preserved.

State and persistence behavior: RNGs are fixed-seed (`42`) for repeatable runs. No generated state is persisted here; `Tester` logs and replays returned crash states.

Dependencies and integration: subclass of `Permuter`, uses C++ `<random>`, `<algorithm>`, `<numeric>`, and CrashMonkey `DiskWriteData`.

Risks: the default constructor does not seed `rand`, while the pointer-taking constructor does; the factory uses the pointer-taking constructor, but other construction paths may be nondeterministic. `std::random_shuffle` is removed in modern C++ standards. In sector mode, `num_sectors` is sampled before coalescing, so it can exceed the coalesced sector vector size; result size may then be larger than filled entries. Fixed seed improves reproducibility but limits exploration diversity across runs unless duplicate rejection changes the sequence.

Test signals: deterministic expected sequences can be asserted for small synthetic epoch sets. Tests should include empty epochs, barrier-ending epochs, duplicate sector offsets, and full-bio versus sector mode.
