## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/fs/SpaceUsageSource.java

Purpose: interface for components that report directory or volume capacity, available space, and used space.

Important APIs: `getUsedSpace`, `getCapacity`, `getAvailable`, default `snapshot`, static `UNKNOWN`, and immutable nested `Fixed` implementation.

Control flow: default `snapshot` calls the three measurement methods and stores them in a `Fixed`. `Fixed` clamps available space to `0..capacity-used` and returns itself for snapshot. State/persistence: implementations may be live; `Fixed` is immutable point-in-time state.

Dependencies: HDDS audience/stability annotations and Java `UncheckedIOException`. Integration points: datanode volume accounting, tests, and disk usage caching. Risks: `Fixed` does not clamp negative used or capacity, so invalid inputs can produce odd values; live implementations may throw unchecked I/O. Test signals: snapshot consistency, clamping behavior, `UNKNOWN`, immutable snapshot, and propagation of unchecked I/O from implementations.
