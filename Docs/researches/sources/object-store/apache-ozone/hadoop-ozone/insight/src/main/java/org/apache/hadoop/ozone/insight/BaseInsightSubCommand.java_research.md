<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/BaseInsightSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/BaseInsightSubCommand.java

Purpose: shared base for picocli insight subcommands. It resolves insight names to concrete `InsightPoint` implementations and maps `Component` objects to HTTP or HTTPS service base URLs.

Important APIs: `getInsight(configuration, selection)` validates a name against `createInsightPoints`. `getHost(conf, component)` prefers component-specified host/port for datanodes and otherwise calls `getComponentAddress` for SCM or OM. `getComponentAddress` chooses HTTP vs HTTPS config keys from `HttpConfig.Policy`, falls back from wildcard bind host to RPC hostname, and preserves the configured/default HTTP service port. `createInsightPoints` registers the stable names consumed by CLI users: SCM node/replica/event/protocol variants, OM key/protocol variants, and datanode pipeline/dispatcher variants.

Control flow: subcommands call `getInsightCommand().getOzoneConf()`, then resolve an insight point by name. Metrics/log/config commands call `getHost` before reaching `/prom`, `/logstream`, `/logLevel`, or `/conf`.

State and persistence: the only state is the injected picocli parent `Insight`. No persistence. `createInsightPoints` instantiates datanode insight points with the active `OzoneConfiguration`, so filters and SCM clients later use the same configuration.

Dependencies and integration: uses Ozone/SCM/OM config keys, `HddsUtils.getHostNameFromConfigKeys`, `HttpConfig`, and all insight point classes. The fallback logic integrates HTTP server bind settings with RPC address settings.

Risks and tests: `getHostOnly` and `getPort` split on the first colon and are fragile for bracketless IPv6 addresses. Unsupported component types throw `IllegalArgumentException`; datanode components must carry host/port. `getInsight` throws a generic `RuntimeException`. `TestBaseInsightSubCommand` covers HTTP-only, HTTPS-only, HTTP-and-HTTPS preference, and fallback-to-RPC behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/BaseInsightSubCommand.java -->
