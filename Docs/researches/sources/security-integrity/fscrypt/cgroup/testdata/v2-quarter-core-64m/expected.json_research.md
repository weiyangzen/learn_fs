# sources/security-integrity/fscrypt/cgroup/testdata/v2-quarter-core-64m/expected.json

## Purpose
Expected result fixture for a cgroup v2 snapshot constrained to one quarter CPU and 64 MiB memory.

## Data and Integration
Contains `{"cpu_quota": 0.25, "memory_limit": 67108864}`. The Go test compares CPU with tolerance 0.001 and memory exactly.

## Risks and Test Signals
This fixture validates fractional quota parsing and byte memory limit parsing for small containers.
