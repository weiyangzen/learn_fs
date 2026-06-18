# sources/security-integrity/fscrypt/filesystem/mountpoint_test.go

## Purpose
This test file validates mountinfo parsing and main-mount selection logic with synthetic mountinfo strings and selected live-system checks.

## Important APIs, Types, and Functions
Helpers `beginLoadMountInfoTest`, `endLoadMountInfoTest`, `loadMountInfoFromString`, and `mountForDevice` isolate global mount maps. Tests cover basic parsing, source device resolution, ignoring non-directory mounts, latest mount precedence, escape/unescape behavior, invalid line rejection, read-only flags, main-mount selection, link creation/resolution, UUID/path fallback, and reload value equality.

## Control Flow
Tests lock `mountMutex`, inject synthetic mountinfo via `readMountInfo`, inspect `mountsByDevice` and `mountsByPath`, then reset initialization state. Link tests use the real test mount and `makeLink`/`getMountFromLink`.

## State and Persistence
The tests mutate global mount cache state and use temporary directories for synthetic mountpoints. Link tests read live UUID state under `/dev/disk/by-uuid` when available but do not write metadata files themselves.

## Dependencies and Integration Points
Depends on live directories such as `/tmp`, `/mnt`, `/home`, and sometimes `/dev/loop0` or a configured test root. It provides regression coverage for `filesystem.FindMount`, `GetMount`, and linked-protector resolution.

## Risks
Some cases skip depending on the host environment. Tests that rely on well-known directories can be sensitive to containers or minimal systems. They do not simulate concurrent callers beyond lock isolation.

## Test Signals
Coverage is broad for bind-mount and container-like mount layouts, including ambiguous topologies where the code must refuse to choose a main mount. It also verifies link fallback when UUID or path is invalid.
