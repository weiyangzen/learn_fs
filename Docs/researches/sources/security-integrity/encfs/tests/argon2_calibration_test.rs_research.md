# sources/security-integrity/encfs/tests/argon2_calibration_test.rs

Purpose: validates the timing model used for Argon2id calibration, ensuring time-cost increases when a low-cost derivation is too fast and remains unchanged when the configured derivation is already slow enough.

Important APIs/types/functions: both tests call `SslCipher::derive_key_argon2id(password, salt, memory_cost, time_cost, parallelism, key_len)`. `test_argon2_calibration_basic` measures one iteration, computes expected calibrated iterations for a one-second target, and asserts the arithmetic. `test_argon2_no_calibration_if_already_slow` measures a heavier parameter set and checks the simulated no-change path when it already exceeds one second.

Control flow: the first test skips the strong timing assertion if a single 8 MiB iteration is already unexpectedly slow, then runs the derived calibrated time cost and requires at least 300 ms as a tolerant lower bound. The second test only asserts equality when the initial 64 MiB, time-cost 3, parallelism 4 derivation exceeds one second; otherwise it prints that calibration would increase time cost.

State and persistence: no files are written. All state is local timing measurements and derived keys.

Dependencies and integration points: depends on `anyhow`, `SslCipher`, and wall-clock timing. It indirectly exercises the Argon2id dependency and default calibration assumptions used by config creation and password upgrades.

Risks: timing tests are inherently environment-sensitive. The basic test tolerates variability heavily, so it verifies arithmetic more than an exact security target. Slow or overloaded CI can turn these into no-op-ish paths.

Test signals: provides a performance-regression signal for Argon2 parameter calibration and a correctness signal that parameter changes actually invoke the KDF successfully.
