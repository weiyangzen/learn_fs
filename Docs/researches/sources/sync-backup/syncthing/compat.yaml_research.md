# sources/sync-backup/syncthing/compat.yaml

## Purpose
This YAML file records release compatibility requirements by Go runtime version. During release builds it is transformed into `compat.json`, which is included with releases and later used by upgrade infrastructure to decide whether a release is compatible with a client's operating system version.

## Important APIs, Types, And Functions
The file is data, not executable code. Each top-level list item has `runtime: go1.xx` and `requirements` mapping OS names to minimum OS versions. The data shape matches `upgrade.ReleaseCompatibility` in `lib/upgrade/upgrade_common.go`, with `Runtime string` and `Requirements map[string]string`. `build.go` reads `compat.yaml`, unmarshals it with YAML, selects the entry whose runtime prefixes `runtime.Version()`, and writes `compat.json`.

## Control Flow
There is no runtime flow inside the YAML. The build flow reads all entries, scans in order for a matching Go runtime, marshals that one entry as JSON, and fails if no runtime matches. Upgrade filtering later treats missing compatibility data as compatible, missing OS entries as compatible, and compares client OS versions against the required version when an OS entry exists.

## State And Persistence Behavior
The source file is maintained in the repository and does not change at runtime. Its build-time output is `compat.json`, a release artifact. Current entries cover Go 1.21 through Go 1.26 and list minimum Darwin, Linux, and Windows versions, with comments documenting upstream Go release-policy sources.

## Dependencies And Integration Points
The file integrates with `build.go` release tooling and `cmd/infra/stupgrades`, which attaches and consumes `compat.json` release metadata. It depends on Go runtime support policy and OS version strings remaining comparable by Syncthing's version comparison logic. It also influences GUI/upgrade behavior because incompatible releases should not be offered to clients below the minimum OS version.

## Risks And Edge Cases
Stale or incorrect minimum versions can either block valid upgrades or offer upgrades that cannot run. The runtime match uses prefix logic against `runtime.Version()`, so future Go versions require an entry or the build fails. Comments cite evolving Go documentation; those comments are useful but not machine-checked. Version string comparison must remain compatible with Darwin kernel versions, Linux kernel versions, and Windows NT version strings.

## Test Signals
The build-time `writeCompatJSON` path is the main validation signal: release builds fail if the current runtime is absent or YAML parsing breaks. Upgrade service tests or manual checks should validate that generated `compat.json` filters releases correctly for representative OS/user-agent versions.
