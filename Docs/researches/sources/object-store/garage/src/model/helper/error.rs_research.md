# sources/object-store/garage/src/model/helper/error.rs

## Purpose
This file defines model-helper errors used by admin and API helper operations. It wraps internal Garage errors, exposes bad-request and not-found conditions, and provides small conversion helpers for mapping `Option`/`Result` failures into client-meaningful errors.

## Important APIs, types, and functions
`Error` variants are `Internal(GarageError)`, `BadRequest`, `InvalidBucketName`, `NoSuchAccessKey`, and `NoSuchBucket`. `From<garage_net::error::Error>` maps network failures into `GarageError::Net`. `OkOrBadRequest` is implemented for `Result<T, E: Display>` and `Option<T>` to attach bad-request context.

## Control flow
Helper functions use `?` to convert low-level errors into `Internal`, and use explicit variants for access key or bucket lookup failures. Validation paths call `ok_or_bad_request` when parser/validation failure should be exposed as a bad client request rather than an internal error.

## State and persistence behavior
This module is stateless and serializable/deserializable. Its error enum is part of helper/RPC boundaries where model-layer errors may cross process boundaries.

## Dependencies and integration points
It depends on `thiserror`, `serde`, `garage_util::error::Error`, and `garage_net::error::Error`. It is imported by bucket, key, locked, K2V seen/rpc, and admin helper paths.

## Risks and edge cases
Overusing `Internal` for user input failures can leak operational messages or produce wrong HTTP status mapping in upper layers. The network conversion collapses all net errors into internal errors, which is appropriate for helper RPCs but may hide retriable/remote failure distinctions. `OkOrBadRequest` formats underlying errors directly into the response.

## Test signals
No local tests. Coverage should verify serialization stability, conversion mapping, and upper-layer HTTP/API error translation for each variant.
