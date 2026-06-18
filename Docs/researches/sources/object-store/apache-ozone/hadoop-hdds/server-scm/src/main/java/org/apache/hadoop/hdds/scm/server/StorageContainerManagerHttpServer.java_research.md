# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/StorageContainerManagerHttpServer.java

Purpose: This class is the SCM-specific `BaseHttpServer` wrapper. It configures the HTTP/HTTPS bind keys, SPNEGO settings, and SCM web context, and registers the SCM DB checkpoint servlet.

Important APIs and types: The constructor calls `super(conf, "scm")`, adds `SCMDBCheckpointServlet` at `OZONE_DB_CHECKPOINT_HTTP_ENDPOINT`, and stores the `StorageContainerManager` in the web app context under `OzoneConsts.SCM_CONTEXT_ATTRIBUTE`. Override methods return SCM-specific keys for HTTP address, HTTPS address, bind hosts, default ports, keytab, SPNEGO principal, enablement, HTTP auth type, and HTTP auth config prefix.

Control flow: `StorageContainerManager.start` constructs this server after RPC services, starts it, and treats failures as non-fatal. The base class uses the overridden keys to decide whether to bind HTTP/HTTPS listeners and how to configure authentication.

State and persistence behavior: This class owns no durable state. Runtime state is the servlet context and the inherited Jetty/HttpServer2 state. The DB checkpoint servlet may read SCM state through the context attribute.

Dependencies and integration points: It integrates SCM with the common Ozone web UI and checkpoint infrastructure. It depends on `ScmConfigKeys`, `SCMHTTPServerConfig`, and the web resources under `src/main/resources/webapps/scm`.

Risks: Misconfigured key overrides can silently bind the wrong address or disable expected auth. Since startup failure is logged but non-fatal, HTTP-only monitoring or DB checkpoint access may be unavailable while SCM itself appears healthy. The context attribute must remain in sync with servlet expectations.

Test signals: Tests should assert the endpoint registration, context attribute, SCM address/default key mapping, HTTP auth prefix, and that `StorageContainerManager` tolerates HTTP startup failure.
