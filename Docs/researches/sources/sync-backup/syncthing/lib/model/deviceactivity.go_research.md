# sources/sync-backup/syncthing/lib/model/deviceactivity.go

## Purpose
Tracks in-flight block requests per remote device and selects the least busy source for new pulls.

## Important APIs, Types, and Functions
`deviceActivity` owns a `map[protocol.DeviceID]int` protected by a mutex. `newDeviceActivity` constructs it. `leastBusy`, `using`, and `done` read or adjust per-device counters.

## Control Flow
`leastBusy` scans an availability slice and returns the index with the lowest current usage count, defaulting to `-1` for empty input. `using` increments the selected device count before a request, and `done` decrements it afterward.

## State and Persistence Behavior
State is in-memory only and process-global in `folder_sendrecv.go` as `activity`. Counters are not persisted and can go negative if `done` is called without matching `using`.

## Dependencies and Integration Points
Depends on `protocol.DeviceID` and the model `Availability` type. `sendReceiveFolder.pullBlock` uses it to spread block requests across available peers.

## Risks
Tie-breaking is order-dependent and favors the first equally idle candidate. The code does not delete zero counters or guard underflow. The global instance means activity spans all folders, which is intentional for balancing but can cross-couple unrelated syncs.

## Test Signals
`deviceactivity_test.go` checks least-busy rotation through increments and decrements across three devices.
