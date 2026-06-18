# sources/storage-engines/wiredtiger/test/cppsuite/src/common/random_generator.cpp

Purpose: Implements thread-local random data generation for test keys, values, and choices.

Important APIs/types/functions: `instance` returns a `thread_local` singleton. `generate_random_string` repeats the chosen character set, shuffles, and truncates. `generate_pseudo_random_string` walks the character set from a random start for more-compressible output. `generate_bool`, `generate_integer`, `get_distribution`, and `get_characters` provide typed random helpers.

Control flow: constructors seed `std::mt19937` from `std::random_device`; invalid `characters_type` reaches `testutil_die`.

State and persistence: each thread owns generator state and distributions; no persisted seed, so runs are not reproducible by default.

Dependencies/integration: used by bounds, database random collection selection, timestamp read selection, and workload generation.

Risks and test signals: lack of deterministic seeding can complicate replay. `generate_random_string` can allocate large temporary repeated strings. Invalid enum use is fatal.
