# sources/user-network-fs/rclone/backend/doi/api/types.go

Purpose: Defines generic DOI resolver API models for handle resolution.

Important APIs, types, and functions: `DoiResolverResponse` contains response code, handle, and values. `DoiResolverResponseValue` models individual handle records. `DoiResolverResponseValueData` carries format and an arbitrary `Value`.

Control flow: No executable logic. `resolveDoiURL` decodes this structure and searches for a value with type `URL` and data format `string`.

State and persistence behavior: Values are transient resolver responses. The resolved URL drives provider detection and endpoint setup, but the response itself is not stored.

Dependencies and integration points: Used by `doi.go` and DOI resolver tests. The `any` value requires runtime type assertion after JSON decoding.

Risks: Resolver responses with non-string URL data, missing URL values, or non-success response codes are rejected. If multiple URL values exist, the current loop keeps the last matching value.

Test signals: Mock resolver tests in `doi_internal_test.go` exercise successful URL resolution and path construction.
