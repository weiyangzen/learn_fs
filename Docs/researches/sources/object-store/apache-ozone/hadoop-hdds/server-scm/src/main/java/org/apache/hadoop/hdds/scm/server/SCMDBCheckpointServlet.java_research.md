# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/SCMDBCheckpointServlet.java

Purpose: `SCMDBCheckpointServlet` exposes a tar.gz checkpoint snapshot of the SCM metadata database through the SCM HTTP server. It inherits checkpoint generation and authorization behavior from `DBCheckpointServlet`.

Important APIs and types: `init()` retrieves `StorageContainerManager` from the servlet context attribute `OzoneConsts.SCM_CONTEXT_ATTRIBUTE` and calls `initialize` with the SCM metadata store, DB checkpoint metrics, admin-authorization flag, empty allowed/denied user lists, and disabled SPNEGO proxy-user style handling.

Control flow: If the SCM context attribute is missing, it logs an error and returns without initializing the servlet. Otherwise the base servlet handles future checkpoint requests.

State and persistence behavior: The servlet itself persists nothing. It reads from the live SCM metadata store and the base servlet materializes checkpoint responses. Authorization is based on SCM admin settings.

Dependencies and integration points: It connects the HTTP server, servlet context, `StorageContainerManager`, SCM metadata store, and SCM metrics. It is used for backup, debugging, and HA/recovery workflows needing DB snapshots.

Risks: If the servlet is registered without the SCM context attribute, it silently remains uninitialized after logging. Checkpoint exposure is sensitive; admin authorization configuration must be correct when Ozone authorization is enabled.

Test signals: Tests should verify initialization with valid SCM, missing-context behavior, passing the correct DB store and metrics to the base servlet, and admin-only access when authorization is enabled.
