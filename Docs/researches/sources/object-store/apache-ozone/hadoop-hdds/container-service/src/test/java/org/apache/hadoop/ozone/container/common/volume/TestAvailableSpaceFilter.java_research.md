# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestAvailableSpaceFilter.java

## Purpose
Tests `AvailableSpaceFilter` decisions and metric increments for healthy space, soft-band admission, and hard minimum free-space rejection.

## Important APIs, Types, And Functions
`AvailableSpaceFilter.test`, `HddsVolume.getReport`, `getFreeSpaceToSpare`, and `VolumeInfoMetrics` soft/hard counters are central.

## Control Flow
Each test builds mocked volume/report values, invokes the filter with required space, and verifies pass/fail plus exact metric interactions. Committed-byte cases prove in-flight allocations affect soft and hard decisions.

## State And Persistence
No durable state exists. Metric increments on mocked metrics are the observable side effects.

## Dependencies And Integration Points
Connects storage location reports, Hdds free-space logic, and container-create admission metrics.

## Risks And Edge Cases
Tests encode arithmetic assumptions around remaining, committed, hard spare, and usable space. Production formula changes require assertion updates.

## Test Signals
Mockito verifies soft-band increments, hard-reject increments, or no metric changes.
