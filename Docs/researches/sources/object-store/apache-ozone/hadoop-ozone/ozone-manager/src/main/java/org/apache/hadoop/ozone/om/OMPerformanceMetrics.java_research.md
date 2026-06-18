# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMPerformanceMetrics.java

Purpose: `OMPerformanceMetrics` is the metrics2 source for Ozone Manager request latency and service-loop performance. It records nano-second request path rates and millisecond service gauges used by OM read/write paths, key operations, object tagging, cleanup services, and snapshot defrag.

Important APIs and types: `register()` registers a source named after the class with `DefaultMetricsSystem`; `unregister()` removes it. Fields are `MutableRate`, `MutableGaugeFloat`, and `MutableGaugeLong` annotated with `@Metric`. Public and package-private accessors expose mutable rate objects for scoped latency capture, while add/set methods record aggregate observations.

Control flow: callers either call direct add/set methods, such as `addLookupLatency`, `setListKeysOpsPerSec`, or `setSnapshotDefragServiceFullLatencyMs`, or retrieve a `MutableRate` and pass it to metric utilities. There is no persistence or internal branching beyond registration.

State and persistence: all state is in the metrics system and is process-local. Counters/rates reset on OM restart. No disk format or DB table is touched.

Dependencies and integration points: used by `OmMetadataReader`, `OmMetadataManagerImpl`, request submit/validation code, delete/open-key cleanup services, and snapshot defrag services. Depends only on Hadoop metrics2 mutable primitives.

Risks: metric method naming must match caller expectations; a likely maintenance trap is `addGetObjectTaggingLatencyNs` recording into the ACL-check metric instead of an overall object-tagging metric because no separate overall field exists. Package-private getters constrain use to the OM package.

Test signals: unit tests can register/unregister without duplicate sources, verify latency methods call the intended metric fields with fake metrics, and check service gauges accept last-iteration values.
