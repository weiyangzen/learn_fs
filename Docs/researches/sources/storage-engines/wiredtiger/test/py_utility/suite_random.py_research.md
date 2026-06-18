# sources/storage-engines/wiredtiger/test/py_utility/suite_random.py

Purpose: deterministic pseudo-random generator for WiredTiger Python test scenarios without global random-module state.

Important APIs and control flow: `suite_random.__init__` accepts zero, one, or two seeds. With no explicit seed it pulls `seedw, seedz` from `abstract_test_case.getseed()`. `rand32()` implements Marsaglia multiply-with-carry updates for two 32-bit seeds and returns a combined 32-bit value. `rand_range(n, m)` bounds the value to `[n, m)`, and `rand_float()` maps the 32-bit integer to `[0, 1)`.

State and persistence behavior: state is only `self.seedw` and `self.seedz`. If either seed is zero, `rand32()` refreshes both from the global test seed source.

Dependencies and integration points: imported by `wtscenario.py` for probabilistic scenario pruning and by any tests needing reproducible randomness.

Risks: `rand32()` calculates updates from local `w`/`z` captured before zero-seed refresh, so a call that starts with a zero seed refreshes object fields but still computes the returned value from the old local values. The generator is deterministic, not suitable for security randomness.

Test signals: repeatable scenario selection under fixed `AbstractWiredTigerTestCase.setupRandom()` seeds is the main validation signal.
