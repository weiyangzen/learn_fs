# sources/object-store/minio/cmd/object-lambda-handlers_test.go

## Purpose
This file provides focused tests for `GetObjectLambdaHandler`. It verifies that a configured lambda webhook response can drive the final S3 response status, headers, and body through the object-lambda route.

## Important APIs, Types, and Functions
- `TestGetObjectLambdaHandler` defines table cases for `206 Partial Content`, `200 OK`, and `400 Bad Request`.
- `runObjectLambdaTest` sets up the object-layer API test harness, an `httptest.Server` lambda target, configures `globalLambdaTargetList`, overrides `getLambdaEventData`, signs a GET request, invokes `api.GetObjectLambdaHandler`, and asserts response details.

## Control Flow
For each case, the helper creates a lambda server that writes route/token headers, a forwarded content-type header, a forwarded status header, and a test body. It builds MinIO lambda webhook config and API gzip config, fetches enabled targets, replaces event generation with deterministic route/token data, signs a request to `/objectlambda/{bucket}/{object}?lambdaArn=...`, then invokes the handler directly with an object API provider.

## State and Persistence Behavior
The tests mutate package globals `globalLambdaTargetList` and `getLambdaEventData` and rely on the object-layer harness for valid credentials and object API initialization. They do not create or persist an actual source object because the event URL is mocked and the lambda body is synthetic. The mock target is process-local and closed with `defer`.

## Dependencies and Integration Points
The test integrates MinIO config loading for lambda webhook targets, signer V4, auth credentials from the object-layer test harness, `httptest`, lambda event structs, and forwarded header constants. It validates the handler independent of normal router dispatch by directly constructing `objectAPIHandlers`.

## Risks and Edge Cases
- The override of `getLambdaEventData` is not restored inside the helper, so additional tests in the same package could inherit it if ordering changes.
- Negative route/token mismatch cases, target lookup failures, malformed forwarded status, and missing forwarded error code/message paths are not covered.
- Error response body for 400 is not asserted; the test only checks status and content type.

## Test Signals
Signals include status code equality, forwarded `Content-Type`, success-body equality for responses below 400, successful lambda target config fetch, V4 signing, and handler operation with object API present.
