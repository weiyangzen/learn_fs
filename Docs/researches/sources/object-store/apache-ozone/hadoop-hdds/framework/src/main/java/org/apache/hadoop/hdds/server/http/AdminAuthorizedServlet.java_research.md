# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/AdminAuthorizedServlet.java

Purpose: `AdminAuthorizedServlet` is a Jetty `DefaultServlet` variant that gates static content access behind `HttpServer2` administrator authorization.

Important APIs/types/functions: it overrides `doGet()` and delegates to `HttpServer2.hasAdministratorAccess(getServletContext(), request, response)`. Only authorized requests call `super.doGet()`.

Control flow: default apps use this servlet for the `/logs` context. If admin access fails, `HttpServer2` writes the forbidden response and the servlet returns without serving content.

State and persistence: no servlet state beyond inherited Jetty state.

Dependencies/integration: depends on `HttpServer2` admin ACL context attributes and Jetty `DefaultServlet`. Integrated by `HttpServer2.addDefaultApps()` when log serving is enabled.

Risks: authorization behavior depends on the servlet context having `CONF_CONTEXT_ATTRIBUTE` and admin ACL attributes set. If Hadoop security authorization is disabled, `HttpServer2.hasAdministratorAccess()` permits access.

Test signals: `HttpServer2` admin access and default-app behavior are covered by `TestHttpServer2` and related base server tests; log context access is indirectly exercised through embedded server setup.
