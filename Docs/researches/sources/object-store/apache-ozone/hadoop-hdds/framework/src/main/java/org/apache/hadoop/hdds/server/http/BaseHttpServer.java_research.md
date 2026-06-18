# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/BaseHttpServer.java

Purpose: `BaseHttpServer` is the abstract superclass for Ozone component web servers. It converts component-specific configuration keys into a configured `HttpServer2`, installs default Ozone servlets, Prometheus/profile support, security, SSL, and bind-address updates.

Important APIs/types/functions: constructor wires the server if `getEnabledKey()` is true. `newHttpServer2BuilderForOzone()` builds HTTP/HTTPS endpoints from `HttpConfig.Policy`. `start()`, `stop()`, and `close()` manage lifecycle. `updateConnectorAddress()` writes real bound addresses back to the mutable config. Protected abstract methods provide component-specific config keys, bind defaults, principal/keytab keys, and auth prefixes. `loadSslConfiguration()` and `loadSslConfToHttpServerBuilder()` bridge SSL config into `HttpServer2.Builder`.

Control flow: construction determines policy, computes bind addresses, disables Hadoop's built-in Prometheus endpoint, configures auth/SPNEGO when HTTP security is enabled, applies X-Frame headers, optionally disables default apps, builds `HttpServer2`, adds Ozone `/conf` and `/logstream`, configures `/prom` with optional bearer token, optionally enables `/prof`, and sets Jetty temp base dir. `start()` starts Jetty, registers the Prometheus sink with Metrics2, and updates connector addresses.

State and persistence: mutable runtime state includes the `HttpServer2`, bind addresses, policy, component name, Prometheus sink, and booleans. It writes resolved listen addresses and HTTP policy back to configuration. It creates a base temp directory under configured `ozone.http.basedir` or metadata dir.

Dependencies/integration: depends on Ozone/Hdds config helpers, `HttpServer2`, `PrometheusMetricsSink`, `PrometheusServlet`, `ProfileServlet`, `HddsConfServlet`, `LogStreamServlet`, SSLFactory, UGI, ACLs, and Metrics2. Extended by OM, SCM, datanode, Recon, and gateway servers.

Risks: security posture changes based on several flags: Hadoop security, Ozone security, HTTP security, auth type, and Prometheus token. A tokenless `/prom` is added as a regular servlet to remain behind auth in secure clusters. Missing SSL resource properties are warned, not always fatal. Base dir creation failure prevents server startup.

Test signals: `TestBaseHttpServer` covers temp dir and connector-address update behavior. Component HTTP server tests cover policy combinations. Prometheus authorization, SSL, and HTTP config tests exercise adjacent behavior.
