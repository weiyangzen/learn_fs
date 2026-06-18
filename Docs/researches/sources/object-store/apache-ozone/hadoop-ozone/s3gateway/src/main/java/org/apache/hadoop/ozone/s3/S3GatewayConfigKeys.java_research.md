# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/S3GatewayConfigKeys.java

Purpose: `S3GatewayConfigKeys` centralizes public, unstable configuration keys and defaults for S3 Gateway HTTP servers, auth, domain routing, buffering, FSO directory behavior, listing behavior, and metrics.

Important APIs and flow: constants define S3 API and web-admin HTTP/HTTPS addresses, bind hosts, default ports, auth config prefixes, Kerberos keytab/principal keys, client buffer size default, virtual-host domain name, FSO directory creation flag, shallow list-keys flag, metrics percentile intervals, and max list keys limit. The class is final and non-instantiable.

State, dependencies, risks, and tests: there is no runtime state or persistence. It integrates with `Gateway`, `S3GatewayHttpServer`, `S3GatewayWebAdminServer`, `VirtualHostStyleFilter`, `EndpointBase`, and bucket listing. Risks are changing key strings/default ports incompatibly and adding behavior without config docs. Test signals come from config-based server startup, routing, and list behavior tests.
