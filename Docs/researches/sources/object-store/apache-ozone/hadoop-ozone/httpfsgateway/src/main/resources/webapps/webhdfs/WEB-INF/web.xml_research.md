# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/resources/webapps/webhdfs/WEB-INF/web.xml

## Purpose
This web descriptor configures the `webhdfs` webapp variant of the HttpFS gateway.

## Important APIs, types, and functions
It registers `HttpFSServerWebApp` as a listener, a Jersey `ServletContainer` scanning `org.apache.ozone.fs.http.server,org.apache.ozone.lib.wsrs`, maps the servlet to `/webhdfs/*`, and configures auth, MDC, hostname, upload content-type, and filesystem release filters.

## Control flow
Servlet context startup initializes the server. All requests pass through the mapped filters and then reach Jersey resources under `/webhdfs/*`.

## State and persistence behavior
The descriptor is deployment metadata only. Runtime state is owned by the listener, filters, and servlet.

## Dependencies and integration points
It wires classes from the HttpFS server package and support classes in this subset. It is distinct from the main webapp descriptor mainly by URL pattern.

## Risks and edge cases
Filter mapping order places `MDCFilter` before `hostnameFilter`, so MDC may not include hostname. Mapping filters to `*` rather than a slash pattern follows the existing descriptor style but should be validated with the target servlet container.

## Test signals
Webapp integration tests or container startup validate descriptor correctness; this subset has no direct descriptor test.
