# sources/object-store/garage/src/api/admin/error.rs

Purpose: defines the Admin API error type and maps admin/domain failures to HTTP status codes, API error codes, headers, and JSON bodies.

Important APIs/types: `enum Error` wraps `CommonError` and adds `NoSuchAdminToken`, `NoSuchAccessKey`, `NoSuchBlock`, `NoSuchWorker`, `NoSuchKey`, and `KeyAlreadyExists`. `commonErrorDerivative!` supplies shared constructors/conversions. `From<HelperError>` maps helper errors into common or admin-specific variants. `Error::code` returns stable API code strings. `ApiError` impl provides HTTP status, CORS/content-type headers, and serialized body.

Control flow and state: no persistence. Error conversion is synchronous and used by handlers and the generic API server. Most not-found variants map to 404; duplicate imported keys map to 409; common errors delegate to shared status logic.

Dependencies/integration: depends on Hyper status/header types, `thiserror`, Garage common error helpers, generic server `ApiError`, and helper-layer errors from `garage_model`.

Risks: the `From<HelperError>` impl has an `unreachable!()` for helper errors not convertible to `CommonError` or `NoSuchAccessKey`; new helper variants could panic if not handled. Error body JSON serialization fallback hides serialization failures behind an InternalError-shaped payload. Code strings are client-visible and should remain stable.

Test signals: cover status/code/body for every variant, CORS headers on errors, helper-error conversion including new helper variants, JSON serialization fallback, and common error delegation.
