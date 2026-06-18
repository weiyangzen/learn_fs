# sources/distributed-fs/tahoe-lafs/src/allmydata/web/common.py

## Purpose
Provides the shared WebAPI utility layer for Tahoe-LAFS Twisted resources. It normalizes request argument handling, format selection, exception-to-HTTP conversion, asynchronous render completion, common text/time/size formatting, child traversal error wrapping, static-resource installation, and private-key parsing for mutable object creation.

## Important APIs, Types, And Functions
`WebError` carries user-facing HTTP errors. Request parsing helpers include `get_arg`, `boolean_of_arg`, `parse_replace_arg`, `get_format`, `get_mutable_type`, `parse_offset_arg`, `get_root`, `should_create_intermediate_directories`, and `get_keypair`. Metadata and JSON helpers include `get_filenode_metadata` and `convert_children_json`. `humanize_exception` and `humanize_failure` map Tahoe domain exceptions to status codes. `exception_to_child` and `render_exception` wrap Twisted `getChild` and render methods with Eliot actions, deferred handling, cancellation, and error pages. `MultiFormatResource` dispatches renderers by query argument. `SlotsSequenceElement` is the local sequence-rendering helper used by many templates.

## Control Flow
Most resources call `get_arg` to merge query args and multipart form fields, then either return a value directly or rely on `@render_exception` to process Deferreds, resources, URLs, bytes, strings, `NOT_DONE_YET`, and failures. `_finish` is the central response finisher: failures are humanized or converted to traceback/error pages, resources are rendered, text is encoded, `DecodedURL` values become redirects, and cancellation after connection loss is ignored. `exception_to_child` similarly wraps traversal methods in `DeferredResource`, mapping exceptions into `ErrorPage` responses.

## State And Persistence
The module has no application persistence. It manages temporary package-resource extraction for static files through an `ExitStack` finalized with the root resource. It also parses request-local RSA private keys from a URL-safe base64 `private-key` argument to support deterministic mutable file/directory creation. Request mutation is limited to response headers, status codes, and cancellation of pending Deferreds when clients disconnect.

## Dependencies And Integration Points
It depends on Twisted Web, Twisted Deferreds, Eliot logging, Hyperlink URLs, importlib package resources, Tahoe interfaces/exceptions, mutable version constants, encoding utilities, and RSA key creation. Nearly every other module in this group imports it. `get_arg` imports `TahoeLAFSRequest` lazily to avoid a circular import with `webish`. `add_static_children` is used by both client and introducer roots to serve packaged static assets.

## Risks And Test Signals
Because this module is a cross-cutting compatibility layer, regressions affect almost every WebAPI endpoint. Risk areas include bytes/str boundary handling in `get_arg`, `url_for_string`, and format dispatch; non-JSON-safe output from `convert_children_json`; request double-finish if resources are not consistently decorated; information exposure from unhandled failures when `Accept` permits HTML traceback; and permissive `when_done` redirects. Test signals include `src/allmydata/test/web/test_common.py`, broad `test_web.py` endpoint coverage, tests for exception mapping, multipart/query precedence, `MultiFormatResource` format errors, cancellation behavior, static assets, and private-key argument handling.
