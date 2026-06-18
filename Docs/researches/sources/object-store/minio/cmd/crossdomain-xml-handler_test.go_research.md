# sources/object-store/minio/cmd/crossdomain-xml-handler_test.go

## Purpose
`crossdomain-xml-handler_test.go` smoke-tests the crossdomain middleware route.

## Important APIs, Types, And Functions
`TestCrossXMLHandler` constructs a MinIO mux router, wraps it with `setCrossDomainPolicyMiddleware`, starts an `httptest.Server`, and performs an HTTP GET for `crossDomainXMLEntity`.

## Control Flow
The test does not register any underlying routes; a successful 200 response proves the middleware intercepts `/crossdomain.xml` before the wrapped router handles it.

## State And Persistence Behavior
Only an in-memory HTTP test server is used. No config files or globals are mutated beyond reading defaults.

## Dependencies And Integration Points
It depends on `github.com/minio/mux`, `net/http/httptest`, and the middleware under test.

## Risks And Test Signals
The test does not close the response body, assert XML content, test custom `globalServerCtxt.CrossDomainXML`, or verify pass-through behavior for other paths. It is a minimal route-existence signal.
