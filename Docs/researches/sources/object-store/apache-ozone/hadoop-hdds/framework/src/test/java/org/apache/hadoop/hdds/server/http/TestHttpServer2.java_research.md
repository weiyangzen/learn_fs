<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestHttpServer2.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestHttpServer2.java

Purpose: verifies `HttpServer2` builder listener idle-timeout configuration.

Important APIs/types/functions: `HttpServer2.Builder`, `setName`, `addEndpoint`, `setIdleTimeout`, `build`, `getListeners`, and Jetty `ServerConnector.getIdleTimeout`.

Control flow: builds an HTTP server bound to localhost port zero with an idle timeout of 60 seconds, then iterates all listeners and asserts Jetty connector idle timeout matches.

State and persistence behavior: no durable state. The server is constructed but not started; listener configuration exists in memory.

Dependencies and integration points: integrates Ozone `HttpServer2` builder with Jetty connector settings.

Risks: narrow coverage; it only verifies configured value propagation, not runtime timeout behavior.

Test signals: asserts every server connector has idle timeout `60000`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestHttpServer2.java -->
