# sources/sync-backup/syncthing/lib/model/deviceactivity_test.go

## Purpose
Tests least-busy selection and counter updates for device request activity.

## Important APIs, Types, and Functions
`TestDeviceActivity` constructs three `Availability` values and exercises `newDeviceActivity`, `leastBusy`, `using`, and `done`.

## Control Flow
The test verifies initial first-device preference, increments selected devices to move preference to the next least-used device, then decrements devices and checks preference changes back.

## State and Persistence Behavior
Only in-memory counters in a fresh `deviceActivity` are mutated. No database, filesystem, or network state.

## Dependencies and Integration Points
Uses `protocol.DeviceID` and model `Availability`, mirroring the puller’s device candidate list.

## Risks
The test is single-threaded, so it does not exercise mutex behavior under concurrent pulls. It also does not cover empty availability returning `-1` or underflow.

## Test Signals
Provides deterministic behavioral coverage for tie-breaking and counter-based balancing.
