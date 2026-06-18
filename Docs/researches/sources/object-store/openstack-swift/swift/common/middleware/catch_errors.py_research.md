# sources/object-store/openstack-swift/swift/common/middleware/catch_errors.py

## Purpose
`catch_errors.py` is top-of-pipeline safety middleware. It assigns a transaction id to every request, catches unhandled exceptions from lower middleware/apps, emits a generic `500` response, and enforces response byte counts so malformed WSGI iterables do not leave client connections in ambiguous states.

## Important APIs, Types, and Functions
`BadResponseLength` marks response-body length mismatches. `ByteEnforcer` wraps an iterable and yields exactly the declared byte count, truncating overlong output and raising on short output. `CatchErrorsContext.handle_request()` performs the transaction-id and exception boundary work. `CatchErrorMiddleware` and `filter_factory()` expose the PasteDeploy filter.

## Control Flow
For each request, `CatchErrorsContext` builds a transaction id, optionally appending truncated `X-Trans-Id-Extra`, stores it in `env['swift.trans_id']`, and updates the logger. It calls the downstream app through `WSGIContext._app_call()`. Exceptions are logged and converted into `HTTPServerError` with both `X-Trans-Id` and `X-Openstack-Request-Id`. Successful downstream responses are wrapped with `ByteEnforcer` for HEAD requests or for a single valid `Content-Length`, then transaction id headers are appended before `start_response()`.

## State and Persistence
Per-request state is held in the WSGI environ, context response fields, and logger transaction id. No durable state is written. `ByteEnforcer` always closes the inner iterable when iteration ends or fails.

## Dependencies and Integration Points
It relies on `generate_trans_id`, `get_logger`, `close_if_possible`, `Request`, `HTTPServerError`, and `WSGIContext`. It should be the first middleware so all downstream errors and malformed response iterators are caught at one boundary.

## Risks and Edge Cases
The bare `except` intentionally catches everything, including unexpected exceptions, so sensitive details are hidden from clients but must be visible in logs. Incorrect downstream `Content-Length` causes `BadResponseLength` during iteration, after headers may already be sent, relying on the WSGI server to close the connection. HEAD responses are forced to zero bytes even if downstream yields data.

## Test Signals
Tests should assert transaction id propagation, `X-Trans-Id-Extra` truncation, generic 500 conversion, header injection on success and failure, exact-length iteration, truncation on overlong bodies, exception on short bodies, HEAD zero-body enforcement, and inner iterable closing.
