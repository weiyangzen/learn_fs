# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerHttpServer.java

Purpose: Tests OM HTTP/HTTPS server startup policy and Jetty temp directory placement.

Important APIs and types: `OzoneManagerHttpServer`, `HttpConfig.Policy`, `URLConnectionFactory`, `KeyStoreTestUtil`, `BaseHttpServer.SERVER_DIR`, `DefaultMetricsSystem`, OM HTTP/HTTPS address and bind config keys, and `/jmx` endpoint probing.

Control flow: `BeforeAll` creates metadata and SSL config directories, generates test keystores, configures HTTP/HTTPS bind addresses on localhost dynamic ports, and builds a URL connection factory. The policy test starts the server for HTTP-only, HTTPS-only, and both, then probes HTTP/HTTPS URLs according to enabled schemes. The Jetty test starts the server and asserts the webserver dir is under the Ozone metadata directory.

State and persistence: writes temp keystore resources and metadata/webserver directories. Server start binds local network sockets and registers metrics.

Dependencies and integration points: integrates OM HTTP server config, Hadoop SSL test infrastructure, metrics system initialization, and client URL connection behavior.

Risks and edge cases: network probing can be environment-sensitive; incorrect address/scheme handling could expose or hide endpoints contrary to policy; Jetty temp dir must not default outside configured metadata dir.

Test signals: successful `/jmx` access only when policy enables the scheme, failed access for disabled schemes, webserver directory existence, and exact `getJettyBaseTmpDir` value.
