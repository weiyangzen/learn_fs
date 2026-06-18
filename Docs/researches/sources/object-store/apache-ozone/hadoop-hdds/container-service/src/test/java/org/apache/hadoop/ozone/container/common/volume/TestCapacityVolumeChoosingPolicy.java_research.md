# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestCapacityVolumeChoosingPolicy.java

## Purpose
Validates capacity-weighted volume selection, out-of-space reporting, policy factory selection, and committed-space accounting.

## Important APIs, Types, And Functions
Uses `CapacityVolumeChoosingPolicy.chooseVolume`, `VolumeChoosingPolicyFactory.getPolicy`, `HddsVolume` committed bytes, and fixed mock space usage sources.

## Control Flow
Setup creates three volumes with equal capacity and different availability, disables reserved space, and pre-commits bytes on one volume. Tests sample 1000 choices, request too much space, check policy factory defaults and overrides, and assert committed-byte increment on selection.

## State And Persistence
State is temporary volume usage plus per-volume committed-byte counters. No durable Ozone metadata is central.

## Dependencies And Integration Points
Uses Ozone volume-choosing policy config, reserved-percent config, mock usage factories, and Hadoop `DiskOutOfSpaceException`.

## Risks And Edge Cases
The 1000-round distribution assertion depends on probabilistic selection. Error-message checks include exact computed available space text.

## Test Signals
Selection counts, factory class equality, exception message content, and committed-byte deltas validate behavior.
