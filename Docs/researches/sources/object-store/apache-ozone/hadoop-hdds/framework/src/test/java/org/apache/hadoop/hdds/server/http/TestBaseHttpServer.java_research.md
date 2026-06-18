<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestBaseHttpServer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestBaseHttpServer.java

Purpose: tests abstract `BaseHttpServer` address/bind-host resolution and runtime config mutation for HTTP/HTTPS listener addresses.

Important APIs/types/functions: `BaseHttpServer`, `HttpConfig.Policy`, `MutableConfigurationSource`, `BaseHttpServer.getBindAddress`, `start`, `stop`, `getHttpAddress`, `getHttpsAddress`, and subclass hooks for address keys, bind host keys, default ports, auth type, and auth config prefix.

Control flow: `setup` establishes a hostname and temp directory. `getBindAddress` creates an anonymous `BaseHttpServer` subclass with test config keys and asserts default bind host plus explicit bind host behavior. `updatesAddressInConfig` creates a concrete `TestingHttpServer`, starts it for each HTTP policy, and verifies the config is updated with actual bound hostname/port for enabled protocols before stopping.

State and persistence behavior: runtime listener state is owned by the server; configuration is mutated in memory with resolved addresses. Temp directories support server construction but no persistent test data is central.

Dependencies and integration points: integrates Ozone mutable configuration, `HttpConfig.Policy`, port allocation, and BaseHttpServer subclass contracts.

Risks: uses free-port allocation and actual server start/stop, so port races are possible. Tests are sensitive to hostname resolution and policy-specific listener enablement.

Test signals: asserts bind address strings for default and configured hosts, and checks HTTP/HTTPS address keys are updated only when the corresponding policy enables the listener.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestBaseHttpServer.java -->
