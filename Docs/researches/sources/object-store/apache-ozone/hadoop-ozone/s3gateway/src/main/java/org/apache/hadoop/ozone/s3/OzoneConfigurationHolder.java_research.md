# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/OzoneConfigurationHolder.java

Purpose: `OzoneConfigurationHolder` bridges CLI-created `OzoneConfiguration` into CDI injection for Jersey resources and filters.

Important APIs and flow: `configuration()` is a static `@Produces` method returning the stored configuration. `setConfiguration` sets the static value only when it is null, supporting mini-cluster/test setup that preloads configuration. `resetConfiguration` clears it for tests.

State, dependencies, risks, and tests: state is a process-static configuration reference. There is no persistence. It integrates with `Gateway`, tracing, filters, and clients needing injected config. Risks include stale configuration across tests or multiple gateway instances in one JVM, and null configuration if startup order is wrong. Tests should reset between cases and assert one-time set semantics.
