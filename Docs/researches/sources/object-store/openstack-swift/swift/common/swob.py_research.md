# sources/object-store/openstack-swift/swift/common/swob.py

## Purpose

`swob.py` is Swift's in-tree WebOb-like WSGI request and response library. It wraps WSGI environ dictionaries, request bodies, response headers, conditional responses, HTTP range handling, WSGI string/byte conversions, and HTTP exception factories. Swift uses it to avoid external WebOb API churn while preserving a familiar interface for middleware, proxy controllers, object/container/account servers, and tests.

## Important APIs, types, and functions

`RESPONSE_REASONS` maps HTTP status codes to reason phrases and default explanatory bodies, including Swift-specific codes such as 499, 507, and 529. `WsgiBytesIO` is a `BytesIO` stand-in for `wsgi.input` that exposes eventlet-style 100-continue methods as no-ops.

Date and header helpers include `date_header_format()`, `parse_date_header()`, `_datetime_property()`, `_header_property()`, `_header_int_property()`, `header_to_environ_key()`, and `HeaderEnvironProxy`. These implement case-insensitive-ish HTTP header access over WSGI environ keys while preserving Python 3 WSGI latin-1 rules.

WSGI conversion helpers (`wsgi_to_bytes()`, `wsgi_to_str()`, `bytes_to_wsgi()`, `str_to_wsgi()`, `wsgi_quote()`, `wsgi_unquote()`, `wsgi_quote_plus()`, and `wsgi_unquote_plus()`) explicitly handle the split between native strings, bytes on the wire, latin-1 WSGI strings, and UTF-8 strings with surrogate escape.

`Range`, `Match`, and `Accept` wrap request headers. `Range` parses `bytes=` headers and converts them into satisfiable half-open ranges with DoS protections (`MAX_RANGES`, `MAX_RANGE_OVERLAPS`, and `MAX_NONASCENDING_RANGES`). `Match` implements ETag set membership with wildcard handling. `Accept.best_match()` parses media ranges, q values, and wildcards to choose a server option.

`Request` exposes WSGI request properties such as `method`, `path_info`, `headers`, `params`, `timestamp`, `range`, `if_match`, `if_none_match`, `accept`, `body`, `message_length()`, `split_path()`, `call_application()`, and `get_response()`. `Request.blank()` constructs test or subrequest environ dictionaries from URLs, headers, body, and request-property keyword arguments. `ensure_x_timestamp()` validates or creates `X-Timestamp` and normalizes it to Swift's internal timestamp format.

`Response` owns response headers, body/app_iter, status, content properties, conditional handling, range serving, default error bodies, relative-location absolutizing, and WSGI callable behavior. It supports single and multipart byte ranges through `app_iter_range`, `app_iter_ranges`, body slicing, `content_range_header_value()`, `content_range_header()`, and `multi_range_iterator()`. `HTTPException` combines `Response` and `Exception`, `wsgify()` adapts request-taking functions to WSGI callables, and `status_map` plus constants such as `HTTPOk`, `HTTPBadRequest`, and `HTTPServiceUnavailable` provide exception factories.

## Control flow

Request construction wraps a caller-provided environ and lazily derives values from it. `Request.blank()` parses the supplied path, fills standard WSGI keys, installs a `WsgiBytesIO`, applies headers through `HeaderEnvironProxy`, and applies supported property kwargs. Request body access consumes `wsgi.input`, then replaces it with a new `WsgiBytesIO` containing the consumed bytes so later consumers can read again.

`Request.call_application()` invokes a WSGI app, captures `start_response`, handles apps that use the returned write callable, reiterates the app iterator if needed to force late `start_response`, and raises if `start_response` never happens. `get_response()` wraps that tuple in a `Response`.

`Response.__call__()` ensures there is a request object, computes `response_iter` once through `_response_iter()`, converts relative `Location` to absolute unless `swift.leave_relative_location` is set, calls `start_response`, and returns the iterable. `_response_iter()` first evaluates conditional request headers, then HEAD behavior, then range behavior, then falls back to app_iter, body, default status body, or an empty body. Failed preconditions close the original iterator without draining it; HEAD uses `friendly_close()` to release resources politely.

Range handling asks the request `Range` object for satisfiable ranges against the current content length. Unsatisfiable ranges become 416 with `Content-Range: bytes */<length>`. Single ranges can be delegated to an app iterator's `app_iter_range()` or served by slicing an in-memory body. Multiple ranges require `app_iter_ranges()` or an in-memory body and produce a multipart/byteranges response with a random boundary and precomputed content length.

## State and persistence behavior

All state is per request/response object and in-memory. `HeaderEnvironProxy` writes directly into the WSGI environ. `Request.params` is cached until the setter changes `QUERY_STRING`. `Request._timestamp` caches parsed timestamp state. `Response.body` may consume and close `app_iter`; assigning `app_iter` closes any previous iterator and may clear content length. `Response.response_iter` is cached after conditional/range processing, so changing headers/body after calling `fix_conditional_response()` or `__call__()` can produce stale output.

There is no durable persistence, but the module is a gateway for protocol state: it mutates headers, environ values, body streams, status, and iterators that higher Swift layers depend on.

## Dependencies and integration points

The module depends on `HeaderKeyDict`, utilities such as `reiterate`, `split_path`, `pairs`, `close_if_possible`, `closing_if_possible`, `config_true_value`, and `friendly_close`, plus Swift timestamp classes and `InvalidTimestamp`. It is integrated across Swift's WSGI pipeline: middleware decorators use `wsgify()`, controllers raise HTTP exception factories, tests use `Request.blank()`, and object responses rely on range and conditional handling.

The code intentionally mirrors parts of WebOb while following Swift-specific protocol needs, including internal timestamps, conditional EC ETag support through `conditional_etag`, reserved-name backend headers, relative-location override, and eventlet-compatible WSGI input behavior.

## Risks and edge cases

This module is protocol-critical. WSGI string conversion must preserve arbitrary bytes from HTTP paths and headers; mistakes can corrupt non-ASCII object names. Header mapping uppercases bytes before converting back to WSGI strings to avoid Python 3 Unicode case-folding surprises. `Request.blank()` rejects unsupported URL schemes and validates latin-1 path compatibility.

Range parsing is a security-sensitive area. The module rejects syntactically invalid range headers by raising `ValueError`, ignores impossible ranges in some cases, and returns an empty range list as the signal for 416 or DoS rejection. Tests must cover suffix ranges, zero-length bodies, overlapping ranges, non-ascending ranges, too many ranges, and delegation to app iterators. Conditional response logic combines ETag and date conditions; ordering changes can alter HTTP semantics.

Response body/app_iter ownership is another risk. Accessing `Response.body` drains streaming iterators into memory. HEAD and failed conditional handling close iterators differently. `Response.__call__()` caches `response_iter`, so response mutation after first call is unsafe. Default error body interpolation uses response attributes for messages such as 507 drive names, so missing attributes become `unknown`.

## Test signals

High-value tests include WSGI byte/string round trips, header environ mapping for content headers and unusual bytes, date parsing/formatting, request path/query construction, body read reset behavior, `message_length()` with content-length and transfer-encoding cases, timestamp validation and normalization, `split_path()` integration, WSGI app invocation paths, Accept best-match sorting and invalid headers, ETag matching, conditional 304/412 responses, HEAD iterator closure, single and multipart ranges over app_iter and body, 416 responses, relative Location absolutizing, `www_authenticate()` realm selection, `wsgify()` exception handling, and every exported HTTP exception factory status.
