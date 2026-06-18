# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneManagerHttpServer.java

## Purpose
`OzoneManagerHttpServer` is a thin `BaseHttpServer` specialization for Ozone Manager. It wires OM-specific HTTP/HTTPS configuration keys, security settings, and servlet endpoints into the shared HDDS HTTP server infrastructure.

## Important APIs, types, and functions
- The constructor calls `super(conf, "ozoneManager")`, registers `ServiceListJSONServlet`, `SnapshotListJSONServlet`, `OMDBCheckpointServlet`, and `OMDBCheckpointServletInodeBasedXfer`, then stores the live `OzoneManager` in the web app context under `OzoneConsts.OM_CONTEXT_ATTRIBUTE`.
- Overrides map base-server hooks to `OMConfigKeys`: HTTP/HTTPS address keys, bind host keys, default ports, Kerberos keytab and SPNEGO principal keys, enabled key, auth type, and auth config prefix.

## Control flow
Construction is the full setup path. Consumers, mainly `OzoneManager.start()` and `restart()`, instantiate it and call `start()` from `BaseHttpServer`. Servlet code later retrieves the OM object from web context attributes to serve service discovery, snapshot lists, and DB checkpoint download endpoints.

## State and persistence behavior
The class itself persists no data. Its endpoints can expose live service state and DB checkpoint data through servlets. Configuration controls whether HTTP is enabled, addresses, bind hosts, HTTPS, SPNEGO/Kerberos, and HTTP auth behavior.

## Dependencies and integration points
It depends on HDDS `BaseHttpServer`, mutable configuration, OM servlet classes, `OzoneConsts` endpoint constants, and `OMConfigKeys`. It is integrated into OM lifecycle as a non-fatal service: OM logs HTTP startup failure and continues.

## Risks and edge cases
Incorrect servlet-to-context wiring would break checkpoint download or service-list APIs. Auth key mismatches could expose endpoints or block administrators unexpectedly. Because HTTP startup failure is non-fatal, callers should not infer OM unavailability from missing web UI alone.

## Test signals
Tests should verify servlet registration paths, context contains the exact OM instance, address/default/auth config keys match OM config constants, HTTPS/SPNEGO settings are honored through `BaseHttpServer`, and OM startup proceeds if this server fails to start.
