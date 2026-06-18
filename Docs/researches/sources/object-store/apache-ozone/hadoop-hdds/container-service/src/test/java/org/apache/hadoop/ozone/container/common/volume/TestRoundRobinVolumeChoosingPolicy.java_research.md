# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestRoundRobinVolumeChoosingPolicy.java

## Purpose
Tests `RoundRobinVolumeChoosingPolicy` ordering, space-aware skipping, out-of-space errors, and committed-space increments.

## Important APIs, Types, And Functions
Uses `RoundRobinVolumeChoosingPolicy.chooseVolume`, `HddsVolume.getCurrentUsage`, `incCommittedBytes`, and `DiskOutOfSpaceException`.

## Control Flow
Setup creates two fixed-usage volumes and disables reserved space. Tests assert alternating zero-size choices, skip the first volume for a larger request, assert oversized requests fail, and confirm committed bytes increase on the selected volume.

## State And Persistence
State consists of policy cursor position and committed-byte counters. Temp volume roots are incidental.

## Dependencies And Integration Points
Uses Hdds volume builders and mock space usage infrastructure.

## Risks And Edge Cases
Exact error message text includes computed available space. Cursor state can make tests order-sensitive if the policy is reused unexpectedly.

## Test Signals
Selected volume equality, exception message content, and committed-byte deltas validate behavior.
