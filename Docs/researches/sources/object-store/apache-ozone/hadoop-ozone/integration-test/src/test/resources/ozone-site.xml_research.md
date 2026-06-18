# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/ozone-site.xml

Purpose: This integration-test `ozone-site.xml` defines common Ozone/HDDS settings used by mini-cluster and shell tests.

Important APIs and types: Configuration keys include mock datanode disk-usage factory, OM transport class, disabled S3 gRPC server, datanode write chunk threads, SCM/OM handler counts, datastream settings, heartbeat intervals, SCM pipeline limit, close-container wait duration, snapshot diff wait time, Ratis log appender byte limits, SCM chunk/block sizes, client stream/datastream buffers, readonly/admin users, and `ozone.directory.deleting.service.interval=2m`.

Control flow: No executable flow. Ozone and Hadoop configuration loaders merge these properties into test configurations. `TestReconfigShell` specifically relies on the directory-deleting interval value when reloading configuration.

State and persistence behavior: Static configuration only; it shapes runtime cluster behavior but does not persist dynamic state itself.

Dependencies and integration points: It integrates with mini-cluster startup, OM/SCM/datanode thread sizing, datastream tests, admin-user authorization tests, snapshot diff tests, and reconfiguration tests. Smaller block/chunk/buffer values make integration tests faster and lower resource consumption.

Risks: The property name for `hdds.container.ratis.log.appender.queue.byte-limit` includes a line break before `</name>`, which may be intentional tolerance or an XML formatting hazard. Changing `ozone.directory.deleting.service.interval` breaks `TestReconfigShell` expectations. Admin user settings are test-only and not production-safe.

Test signals: Signals are indirect: clusters start with mock DU, expected handler/heartbeat/buffer behavior, reconfiguration reloads `2m`, and admin-related tests see `admin` as configured administrator/readonly administrator.
