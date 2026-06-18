# sources/security-integrity/fscrypt/actions/hashing_test.go

## Purpose
Tests and benchmarks passphrase hashing cost calibration from `config.go`.

## APIs and Control Flow
`TestCostsSearch` calls `getHashingCosts` for 100 ms, 200 ms, and 500 ms targets, retimes the selected costs with `timeHashingCosts`, and accepts results within a factor of three. Benchmarks run calibration for 10 ms, 100 ms, and 1 s targets with logging discarded.

## State, Dependencies, and Integration
The tests exercise actual Argon2 hashing and process CPU timing. They indirectly use cgroup-aware CPU and memory limits from `config.go`.

## Risks and Test Signals
The factor-of-three threshold acknowledges noisy machines and CPU scheduling. The test can be expensive or flaky on constrained hosts, but it is the primary regression signal for calibration returning wildly weak or slow parameters.
