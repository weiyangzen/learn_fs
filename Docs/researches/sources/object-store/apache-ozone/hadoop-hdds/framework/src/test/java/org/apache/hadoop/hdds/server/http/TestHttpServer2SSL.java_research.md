<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestHttpServer2SSL.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestHttpServer2SSL.java

Purpose: integration-style tests for `HttpServer2` TLS configuration, including cipher include/exclude lists, protocol restrictions, default TLS connectivity, and propagation of Hadoop `SSLFactory` enabled-protocol settings into Jetty.

Important APIs/types/functions: `HttpServer2.Builder`, `keyPassword`, `keyStore`, `trustStore`, `excludeCiphers`, `includeCiphers`, `start`, `stop`, `getListeners`, `SSLFactory.SSL_ENABLED_PROTOCOLS_KEY`, `SSL_ENABLED_PROTOCOLS_DEFAULT`, `KeyStoreTestUtil`, `HttpsURLConnection`, `SSLSocketFactory`, `SSLSocket`, and a local `ConstrainedSSLSocketFactory`.

Control flow: class-level setup creates test keystore/truststore config and loads server SSL settings. Tests build HTTPS servers with specific cipher/protocol constraints, start them, connect to `/jmx` using a constrained client socket factory, and assert either HTTP 200 or handshake failure. Protocol propagation tests inspect Jetty `SslContextFactory.Server` include/exclude protocol arrays directly.

State and persistence behavior: setup writes temporary keystore/truststore files and SSL config resources, cleaned in `tearDown`. Each test starts/stops an embedded HTTPS server and opens network connections to localhost.

Dependencies and integration points: integrates Ozone `HttpServer2`, Hadoop `SSLFactory` config, Jetty SSL context factories, Java SSL/TLS sockets, trust-manager initialization, and HTTPS URL connections.

Risks: TLS tests are environment-sensitive because supported ciphers/protocols vary by JDK/security policy. Local port allocation and network timing can be flaky. Exact cipher names require JDK support.

Test signals: asserts excluded ciphers reject clients, included ciphers accept matching and reject other ciphers, TLSv1.2-only server accepts TLSv1.2 and rejects TLSv1.1, default config accepts connections, configured/default enabled protocols are included in Jetty, and selected protocol is not excluded.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/http/TestHttpServer2SSL.java -->
