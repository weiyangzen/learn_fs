## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/AbstractContainerScannerMetrics.java

Purpose: Defines shared Hadoop Metrics2 counters and gauges for container scanners.

Important APIs and functions: Tracks current-iteration containers scanned, current-iteration unhealthy containers, and total scan iterations since restart. Increment, getter, and reset methods wrap `MutableGaugeInt` and `MutableCounterInt`. `unregister()` removes the metrics source, and `getName()` exposes its name.

Control flow and state: Subclasses register concrete instances with a `MetricsSystem`, then this base owns the mutable metric fields injected by Metrics2. Reset methods decrement gauges by their current value.

Persistence and dependencies: Metrics are in-memory telemetry, not persistent state. Depends on Hadoop Metrics2 annotations, `MetricsSystem`, and mutable metric types.

Risks: Reset-by-decrement assumes no concurrent increments during reset. `unregister()` must be called once scanner lifecycle ends to avoid duplicate source registration. Metrics fields are initialized by Metrics2 registration, so manual construction without registration can leave null fields.

Test signals: Metrics registration, increments and resets, unregister on scanner shutdown, subclass metric inheritance, duplicate registration names, and concurrent scan metric updates if scanners become multi-threaded.
