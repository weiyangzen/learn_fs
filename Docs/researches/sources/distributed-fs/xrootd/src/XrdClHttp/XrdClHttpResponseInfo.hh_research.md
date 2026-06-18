# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpResponseInfo.hh

## Purpose

This header defines `XrdClHttp::ResponseInfo`, the opt-in container for raw HTTP response headers collected during an operation, including redirects.

## Important APIs, types, and functions

`HeaderValues` is a vector of values for repeated headers. `HeaderMap` maps canonical, case-sensitive header names to value lists. `HeaderResponses` is a vector of header maps, one per HTTP response observed by the operation. `AddResponse` appends a completed header map, and `GetHeaderResponse` returns the collected responses by const reference.

## Control flow

`CurlOperation::Header` creates a `ResponseInfo` lazily when the first header block finishes and pushes the parser's header map. Operation-specific response wrappers then move the `ResponseInfo` into returned XRootD response objects when the `XrdClResponseInfo` property is enabled.

## State and persistence behavior

State is per response object and memory-only. Header key lookup is intentionally case-sensitive after local canonicalization, so callers must use the canonical header spelling documented by the header.

## Dependencies and integration points

This is consumed by connection callouts, header response wrappers, `CurlOperation`, and users of the public response-info property. It is small but ABI-sensitive because it is exposed to plugin consumers.

## Risks and edge cases

The container preserves multiple response blocks but does not label which block is a redirect versus final response except by order. It stores all headers accepted by `HeaderParser`, which may exclude malformed headers. Consumers must use canonical header keys or miss values.

## Test signals

Tests should verify repeated header storage, redirect header ordering, canonical key expectations, and movement into derived response objects. No direct tests were found.
