# sources/storage-engines/foundationdb/fdbserver/workloads/KillRegion.cpp

## Purpose
Simulation-only force-recovery workload that disables regions, kills data centers, and verifies recovery into a usable single-region configuration.

## Important APIs, types, and functions
`KillRegionWorkload` derives from `TestWorkload`, sets `fdbSimulationPolicyState().usableRegions = 1`, disables all other failure injection, and uses `_setup`, `waitForStorageRecovered`, and `killRegion`. It calls `ManagementAPI::changeConfig`, `waitForPrimaryDC`, `forceRecovery`, `getDatabaseConfiguration`, and simulator data-center kill APIs.

## Control flow
Client 0 first disables the primary and waits for remote DC `"1"` to become primary. During start, it may disable remote and restore original region settings, waits a random fraction of `testDuration`, kills data centers `"0"`, `"2"`, and `"4"` with random destructive kill types, then force-recovers using DC `"1"`. If the configuration still has multiple usable regions, it repeatedly configures primary disablement and anti-quorum until storage recovers, then sets `usable_regions=1`.

## State and persistence behavior
The workload mutates cluster configuration and simulated process liveness. It does not write user keys, but it can delete/reboot simulated data-center processes and changes recovery/region metadata.

## Dependencies and integration points
Depends on simulated networking, simulation policy state, management API config changes, recovery state from `dbInfo`, connection-record based force recovery, and database configuration reads.

## Risks and test signals
This is intentionally disruptive and incompatible with other failure injectors. Risks include hard-coded DC IDs, force-kill requirements, and long waits for storage recovery. `check` always returns true, so signals are successful actor completion and trace events through force-recovery phases.
