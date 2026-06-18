# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/package-info.java

Purpose: this package-info documents `org.apache.hadoop.hdds.server.http` as the servlets and utilities for embedded Ozone service web servers.

Important APIs/types/functions: no runtime API is declared here. The package contains the embedded server wrapper (`HttpServer2`), component base class (`BaseHttpServer`), security/quoting/cache filters, diagnostics servlets, and Prometheus/Ratis metrics exporters.

Control flow: none in this file.

State and persistence: none.

Dependencies/integration: package is the HTTP surface for OM, SCM, datanode, Recon, and related components.

Risks: none in this file; package-level risk centers on admin endpoint exposure and correct HTTP security configuration.

Test signals: package behavior is covered by HTTP server, SSL, base server, Prometheus, profile, and HTML quoting tests.
