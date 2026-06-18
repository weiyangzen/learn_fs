# sources/security-integrity/fscrypt/cgroup/testdata/v2-two-cores-256m/expected.json

## Purpose
Expected result fixture for a cgroup v2 snapshot constrained to two CPUs and 256 MiB memory.

## Data and Integration
Contains `{"cpu_quota": 2.0, "memory_limit": 268435456}`. It checks whole-number quota parsing and larger memory limit propagation.

## Risks and Test Signals
This fixture ensures the parser returns floating quotas even for integer CPU limits and feeds confidence for container-aware Argon2 calibration.
