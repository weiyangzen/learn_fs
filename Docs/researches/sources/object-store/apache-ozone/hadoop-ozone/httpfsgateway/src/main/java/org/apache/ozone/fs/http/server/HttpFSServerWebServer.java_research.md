# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/fs/http/server/HttpFSServerWebServer.java

## Purpose
`HttpFSServerWebServer` is the standalone launcher and Jetty/HttpServer2 wrapper for the HttpFS gateway.

## Important APIs, Types, and Functions
Static initialization registers `httpfs-default.xml` and `httpfs-site.xml` as Hadoop configuration resources. Constructor options include HTTP host/port, SSL enablement, administrators ACL, and deprecated environment-variable overrides. The constructor builds `HttpServer2` with the `webhdfs` name, endpoint, SSL config, auth filter prefix, ACL, and filtered initializer configuration. Lifecycle methods are `start()`, `join()`, `stop()`, and `getUrl()`. `main()` creates Ozone and SSL configurations, logs startup/shutdown metadata, constructs the server, starts it, and joins.

## Control Flow
Construction first maps legacy `HTTPFS_*` environment variables into configuration with warnings, determines HTTP vs HTTPS scheme, builds an endpoint URI, removes default Hadoop auth/proxy filter initializers from configured initializers so HttpFS can supply its own auth configuration, and builds the server. Runtime is then delegated to `HttpServer2`.

## State and Persistence Behavior
The class holds the built `HttpServer2` and selected scheme. It does not persist data. It reads environment variables and configuration resources at startup.

## Dependencies and Integration Points
It depends on Ozone configuration, Hadoop `HttpServer2`, SSLFactory, ACLs, auth filter initializers, legacy configuration source wrappers, and Ozone version startup logging.

## Risks and Edge Cases
Deprecated environment variables still override XML properties, which can surprise operators. `getUrl()` returns null until a connector address exists. Removing configured initializers by exact class name assumes comma-separated configuration without class aliases. SSL config must be valid when enabled.

## Test Signals
No direct test in this subset. Useful tests would validate env override mapping, initializer filtering, URL generation, and SSL/HTTP endpoint construction.
