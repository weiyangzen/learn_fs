# sources/object-store/minio/cmd/object-lambda-handlers.go

## Purpose
This file implements S3 Object Lambda GET handling. Instead of returning object bytes directly, it constructs an object-lambda event with a presigned input S3 URL, sends it to a configured lambda/webhook target, validates the target's route/token response, forwards selected headers and status, maps lambda-declared errors into S3 API errors, and streams the transformed body to the client.

## Important APIs, Types, and Functions
- `getLambdaEventData` builds a `levent.Event` containing `GetObjectContext`, the original user request, and user identity. It uses MinIO client presigning with temporary credentials and forwards supported GET/HEAD query parameters plus `partNumber`.
- `fwdHeadersToS3` copies response headers with the `x-amz-fwd-header-` prefix to the client response without the prefix.
- `fwdStatusToAPIError` converts forwarded lambda status and error headers into `APIError` values for status codes >= 400.
- `GetObjectLambdaHandler` is the HTTP handler on `objectAPIHandlers`.

## Control Flow
The handler creates an audit context, checks the object layer is initialized, extracts bucket/object path variables, authorizes `policy.GetObjectAction`, looks up the configured lambda target by `lambdaArn`, builds event data, and sends it to the target. It then validates that `x-amz-request-route` equals the generated route and that `x-amz-request-token` matches the generated token with constant-time comparison. If the target supplies `x-amz-fwd-status`, the handler parses it as the client status. Forwarded headers are copied, forwarded error headers can terminate with an S3 XML error, gzip is disabled when global API config says object gzip is off, and the lambda body is copied to the client.

## State and Persistence Behavior
The handler itself does not persist object data. It relies on presigned access to the underlying object store and on `globalLambdaTargetList`, global endpoint/TLS settings, site region, remote transport, and global API gzip configuration. `getLambdaEventData` derives the output token from access key plus presigned query string, so token validity is tied to the generated URL and credentials.

## Dependencies and Integration Points
It integrates with MinIO auth, policy checks, mux variables, lambda target configuration, MinIO Go client presigning, shortuuid route generation, SHA-256 token generation, response header constants in `internal/http`, audit logging, and gzip middleware behavior. It is reached through the object-lambda router path rather than normal object GET routing.

## Risks and Edge Cases
- The duration clamp in `getLambdaEventData` always sets one hour because the condition is `duration > time.Hour || duration < time.Hour`; only exactly one hour would avoid reassignment.
- `io.Copy` return errors are ignored after headers are written, so downstream write/read failures are not translated into API errors.
- Response trust is centered on route/token validation; any mismatch produces invalid request/token errors before body forwarding.
- Forwarded status parsing can fail and returns a synthetic `LambdaFunctionStatusError`.
- Global mutable `getLambdaEventData` is reassigned in tests and must be restored if future tests share process state.

## Test Signals
The paired test file mocks a lambda target and overrides event generation, checking 200, 206, and 400 paths, forwarded content type, body forwarding on success, request signing, target lookup, and disabled gzip configuration.
