# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/webapp/WEB-INF/web.xml

## Purpose
This is the main HttpFS webapp descriptor, wiring server startup, Jersey resources, and request filters.

## Important APIs, types, and functions
It registers `HttpFSServerWebApp`, Jersey `ServletContainer` scanning `org.apache.ozone.fs.http.server,org.apache.ozone.lib.wsrs`, maps the servlet to `/*`, and maps authentication, MDC, hostname, upload content-type, and filesystem release filters to all requests.

## Control flow
The listener initializes/destroys the server with the servlet context. Requests pass through filters before Jersey dispatch.

## State and persistence behavior
The file is static deployment metadata only.

## Dependencies and integration points
It binds web container configuration to the service framework and REST provider packages. Compared with `resources/webapps/webhdfs/WEB-INF/web.xml`, this variant exposes the Jersey servlet at the app root.

## Risks and edge cases
The same filter-order concern exists: MDC is configured before hostname. Root mapping means static or auxiliary paths in the same webapp may also hit Jersey unless separately handled.

## Test signals
Container integration and REST endpoint tests validate this descriptor; no direct test is present here.
