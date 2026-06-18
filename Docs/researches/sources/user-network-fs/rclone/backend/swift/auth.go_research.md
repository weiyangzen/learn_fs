# sources/user-network-fs/rclone/backend/swift/auth.go

## Purpose

`auth.go` defines a wrapper authenticator for the Swift backend that can override storage URL and auth token while delegating the rest of authentication behavior to an underlying Swift authenticator.

## Important APIs, Types, and Functions

`auth` stores `parentAuth`, `storageURL`, and `authToken`. `newAuth` constructs the wrapper. Methods implement `swift.Authenticator`: `Request`, `Response`, `StorageUrl`, `Token`, and `CdnUrl`. `Expires` implements `swift.Expireser` when the parent supports it.

## Control Flow

If a parent authenticator exists, request/response handling is delegated. `StorageUrl` and `Token` return configured override values when non-empty; otherwise they delegate to the parent or return empty strings. `Expires` type-asserts the parent to `swift.Expireser`.

## State and Persistence Behavior

The wrapper is immutable after construction and stores no persistent state. It preserves fixed token/storage URL overrides across re-authentication.

## Dependencies and Integration Points

It depends on `github.com/ncw/swift/v2`. `swiftConnection` uses it when user-supplied `storage_url` or `auth_token` should override values discovered during `Authenticate`.

## Risks and Edge Cases

If `parentAuth` is nil and no overrides are set, methods return empty values and no auth request is made. Expiry information is unavailable unless the parent provides it. Overrides can intentionally bypass service-catalog values, so stale tokens or URLs are user responsibility.

## Test Signals

Useful tests construct wrappers with nil and mock parents to verify override precedence, delegation, expiry passthrough, and behavior after Swift connection authentication.
