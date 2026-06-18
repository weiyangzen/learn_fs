# sources/security-integrity/fscrypt/cli-tests/t_passphrase_hashing.sh

## Purpose
Integration smoke test that passphrase hashing difficulty configured by `fscrypt setup --time` is not trivially fast.

## Control Flow and Integration
Runs global setup with default 1s hashing and encrypts five directories, expecting elapsed time greater than 3s. Then runs setup with `--time=5s`, encrypts one directory, and again expects more than 3s.

## State and Risks
Exercises config recreation, hashing cost calibration, and actual custom protector creation. Timings are intentionally loose but can still be sensitive to extremely fast or loaded systems.

## Test Signals
Protects against accidental near-zero Argon2 costs in user-facing setup.
