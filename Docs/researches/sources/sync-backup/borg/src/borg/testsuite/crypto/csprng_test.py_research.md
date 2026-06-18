# sources/sync-backup/borg/src/borg/testsuite/crypto/csprng_test.py

Purpose: validates deterministic and range-correct behavior of Borg's keyed `CSPRNG` helper.

Important APIs and control flow: tests instantiate `CSPRNG` with two fixed 32-byte keys. They compare deterministic `random_bytes` output for same-key instances, verify different keys differ, exercise byte lengths from 1 through 10000, call `random_int` over small, large, power-of-two, and adjacent bounds, and require `ValueError` for non-positive bounds. Shuffle tests verify deterministic same-key permutations, different-key differences, continued-stream differences, and large-list permutation preservation.

State and persistence: no persistent state. The generator has internal stream/counter state visible through the "same RNG used again gives a different shuffle" assertion.

Dependencies and integration points: depends on `borg.crypto.low_level.CSPRNG` and pytest. The generator is relevant to chunk-size obfuscation and any deterministic keyed randomization inside Borg.

Risks: statistical tests over 10000 bytes use fixed but probabilistic uniformity thresholds. A correct CSPRNG with a changed algorithm could still break deterministic-vector expectations indirectly through distribution thresholds or shuffle order.

Test signals: deterministic equality for same key, inequality for different keys, valid bounds, permutation preservation, byte-count distribution, and bit-count distribution.
