# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/S3GatewayHttpServer.java

Purpose: `S3GatewayHttpServer` adapts the HDDS `BaseHttpServer` to serve the S3-compatible API port.

Important APIs and flow: it disables default web apps, sets a common filter-priority spacing constant, and maps BaseHttpServer key lookups to S3G-specific address, bind host, HTTPS, keytab, SPNEGO principal, enablement, and HTTP auth config keys.

State, dependencies, risks, and tests: server state is owned by `BaseHttpServer`; this subclass only supplies configuration names. It integrates with `Gateway`, servlet/Jersey deployment, and security config. Risks are wrong key mapping causing bind failures or SPNEGO misconfiguration, and disabling default apps requiring the web-admin server to expose static/admin content. Tests are server startup/address assertions under configured and default ports.
