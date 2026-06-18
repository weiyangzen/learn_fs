# sources/security-integrity/fscrypt/bin/snapshot-cgroup

## Purpose
Captures the minimal live cgroup v2 files needed by cgroup package tests into a mock root tree.

## APIs and Control Flow
The script requires exactly one output directory. It copies `/proc/self/cgroup`, extracts the v2 group path with `awk -F: '/^0::/'`, builds `/sys/fs/cgroup${group}`, and copies `cpu.max` and `memory.max` if present.

## State, Dependencies, and Integration
Writes a `proc/self/cgroup` and `sys/fs/cgroup/...` subtree under the output directory. It is invoked by `gen-cgroup-testdata` inside Docker containers.

## Risks and Test Signals
It assumes cgroup v2 entries are present and does not fail if limit files are absent. Missing files intentionally let the Go package report `ErrNoLimit`.
