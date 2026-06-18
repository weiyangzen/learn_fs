# sources/security-integrity/fscrypt/cgroup/cgroup_test.go

## Purpose
Tests cgroup v2 resource limit parsing using synthetic v1 input, captured v2 fixtures, and optional live environment expectations.

## APIs and Control Flow
`writeFile` creates fixture files. `TestCgroupV1Unsupported` writes v1-style `/proc/self/cgroup` and expects `ErrV1Detected`. `TestWithRootFromTestdata` iterates fixture directories, unmarshals `expected.json`, constructs `NewFromRoot`, and checks `CPUQuota` and `MemoryLimit`, using `ErrNoLimit` when JSON values are null. `TestIntegrationCgroupLimits` reads expected values from environment and tests the live system.

## State, Dependencies, and Integration
Uses `cgroup/testdata` captured by shell scripts. Optional live tests are controlled by `CGROUP_EXPECTED_CPU_QUOTA` and `CGROUP_EXPECTED_MEMORY_LIMIT`.

## Risks and Test Signals
Snapshot tests are deterministic and cover no-limit and limited cases. They do not directly unit-test malformed `cpu.max` or `memory.max`, but error paths are simple parser returns.
