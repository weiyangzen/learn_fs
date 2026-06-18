# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ha/OMHAMetrics.java

Purpose: `OMHAMetrics` publishes metrics describing an OM node's HA identity and whether it is currently the leader.

Important APIs and types: It implements `MetricsSource`, registers under source name `OMHAMetrics`, and exposes static `create` and `unRegister`. `getMetrics` emits a `NodeId` tag and `OzoneManagerHALeaderState` gauge with value 1 for leader and 0 for follower.

Control flow: On each metrics collection, it compares `currNodeId` and `leaderId`, updates an internal info holder, emits the tag/gauge, and ends the record.

State and persistence behavior: State is process-local metric state. No persistent data is written.

Dependencies and integration points: It integrates with Hadoop metrics2, `DefaultMetricsSystem`, and OM HA leadership tracking.

Risks and test signals: `leaderId` is only constructor state in this class, so callers need a new instance or external update path if leadership changes are not represented elsewhere. Registration uses a fixed source name. Tests should cover leader/follower gauge values, node ID tag, unregister/re-register, and duplicate registration behavior.
