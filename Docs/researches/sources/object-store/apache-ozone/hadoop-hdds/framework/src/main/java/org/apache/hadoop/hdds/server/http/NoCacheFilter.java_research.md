# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/http/NoCacheFilter.java

Purpose: `NoCacheFilter` adds no-cache response headers to servlet contexts served by `HttpServer2`.

Important APIs/types/functions: `doFilter()` casts the response to `HttpServletResponse`, sets `Cache-Control: no-cache`, `Expires`, `Date`, and `Pragma: no-cache`, then delegates to the filter chain. `init()` and `destroy()` are no-ops.

Control flow: `HttpServer2` installs this filter on the main web app and default contexts. Each request receives cache-control headers before the target servlet executes.

State and persistence: stateless.

Dependencies/integration: depends on Java Servlet filter APIs. Integrated through `HttpServer2.createWebAppContext()`, `addNoCacheFilter()`, and `addContext()`.

Risks: forcibly disables caching even for static resources, which is safer for admin/status pages but can reduce browser/cache efficiency. The response cast assumes HTTP servlet usage.

Test signals: indirect coverage through `HttpServer2` tests and embedded server context setup.
