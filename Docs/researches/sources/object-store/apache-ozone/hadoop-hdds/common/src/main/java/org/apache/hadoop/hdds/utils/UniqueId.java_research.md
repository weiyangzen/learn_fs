# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/UniqueId.java

## Purpose
Generates process-local long IDs by combining current time milliseconds with a 16-bit counter.

## Important APIs, Types, And Functions
The class is a non-instantiable utility. `next()` is synchronized, reads `HddsUtils.getTime()`, left-shifts it by `Short.SIZE`, and appends `offset++ & 0xFFFF`.

## Control Flow
Each call validates that the high 16 bits of the time value are clear, returns `(time << 16) | lowCounter`, or throws if time is too large.

## State And Persistence
State is the static `offset` counter in memory. IDs are not persisted and are not globally coordinated across processes.

## Dependencies And Integration Points
Depends on `HddsUtils.getTime()`. Tests and helper code such as `ContainerTestHelper` use it for local IDs.

## Risks
More than 65,536 calls in the same millisecond wrap the low counter and can collide. Clock rollback can produce lower or duplicate IDs. Cluster-wide uniqueness is not guaranteed.

## Test Signals
Useful tests are monotonic-ish generation under normal load, high-throughput same-millisecond collision behavior with a mocked clock, and invalid future time handling.
