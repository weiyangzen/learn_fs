# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ha/TestOMHAMetrics.java

Purpose: Tests leader-state gauge behavior in `OMHAMetrics`.

Important APIs and types: `OMHAMetrics.create`, `getMetrics`, `getOmhaInfoOzoneManagerHALeaderState`, `MetricsCollectorImpl`, and metrics unregister lifecycle.

Control flow: one test creates metrics with local node equal to leader ID and expects leader state `1`; another creates metrics with a different leader ID and expects `0`. `AfterEach` unregisters static metrics state.

State and persistence: metrics are in-memory Hadoop metrics sources. No durable state.

Dependencies and integration points: OM HA metrics are consumed by monitoring systems to distinguish leader and follower nodes.

Risks and edge cases: static metrics registration can leak between tests without unregister; leader-state comparison depends on exact node ID strings.

Test signals: metric value `1` for leader, `0` for follower, after invoking `getMetrics`.
