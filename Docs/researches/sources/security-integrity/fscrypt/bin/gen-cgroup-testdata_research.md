# sources/security-integrity/fscrypt/bin/gen-cgroup-testdata

## Purpose
Regenerates cgroup v2 test fixtures by running `snapshot-cgroup` inside Docker containers with known CPU and memory limits.

## APIs and Control Flow
The script changes to repo root, defines `testdata` and `snapshot_script`, and defines `generate(name, cpu_quota, memory_limit, docker args...)`. Each case removes/recreates its fixture directory, runs `docker run` with mounted snapshot script and output directory, then writes `expected.json`. It generates two limited containers and one no-limit fixture.

## State, Dependencies, and Integration
Writes under `cgroup/testdata`. Requires Docker and a host using cgroup v2. Integrates with `cgroup_test.go`, which reads the generated snapshots and expected JSON.

## Risks and Test Signals
Fixture generation is host/runtime dependent; Docker cgroup configuration must match expectations. The expected JSON is manually provided from function arguments, so a Docker behavior change could produce snapshot files inconsistent with expected limits.
