# sources/security-integrity/fscrypt/cgroup/cgroup.go

## Purpose
Reads CPU and memory limits from Linux cgroup v2. The actions config calibrator uses this to avoid choosing Argon2 costs based on host resources when running inside containers.

## APIs, Types, and Control Flow
Exports `ErrNoLimit`, `ErrV1Detected`, `Cgroup`, `New`, `NewFromRoot`, `CPUQuota`, and `MemoryLimit`. `NewFromRoot` parses `proc/self/cgroup`, rejects any v1 controller entries, finds the v2 `0::` path, and builds a cgroup directory under `sys/fs/cgroup`. `CPUQuota` reads `cpu.max` and parses either `max` or quota/period into fractional CPUs. `MemoryLimit` reads `memory.max` and parses bytes or `max`.

## State, Dependencies, and Integration
The package is read-only and filesystem based. `NewFromRoot` enables deterministic tests with captured fixture trees. Integration with `actions/config.go` feeds `effectiveCPUCount` and `memoryBytesLimit`.

## Risks and Test Signals
The implementation intentionally supports only cgroup v2 and returns `ErrV1Detected` on any v1 controllers. `parseCPUMax` allows a single numeric field and defaults period to 100000, matching kernel defaults. Tests cover v1 rejection, real snapshots, and optional live integration.
