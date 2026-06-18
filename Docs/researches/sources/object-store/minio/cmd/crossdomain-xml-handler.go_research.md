# sources/object-store/minio/cmd/crossdomain-xml-handler.go

## Purpose
`crossdomain-xml-handler.go` provides middleware that serves a Flash/Acrobat-style `crossdomain.xml` policy at `/crossdomain.xml`.

## Important APIs, Types, And Functions
`crossDomainXML` stores the default permissive XML policy matching S3 behavior. `crossDomainXMLEntity` is the request path. `setCrossDomainPolicyMiddleware` wraps an `http.Handler`, serves `globalServerCtxt.CrossDomainXML` when configured, otherwise serves the default XML, and delegates all other paths.

## Control Flow
For every request, the middleware selects the configured/default XML string, compares `r.URL.Path` to `/crossdomain.xml`, writes the XML response and returns on match, or calls the next handler otherwise.

## State And Persistence Behavior
No persistent state is written. It reads `globalServerCtxt.CrossDomainXML`, which is populated from the `--crossdomain-xml` file in `common-main.go`.

## Dependencies And Integration Points
It integrates with the HTTP middleware chain and server context CLI option. It exists for compatibility with legacy cross-domain client behavior.

## Risks And Test Signals
The default policy is permissive. The middleware does not set an explicit content type. `crossdomain-xml-handler_test.go` only checks that `/crossdomain.xml` returns HTTP 200, not body or custom XML behavior.
