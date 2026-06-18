## sources/object-store/minio-mc/pkg/probe/wrapper.go

Purpose: adapts `*probe.Error` to the standard `error` interface and back. Important APIs are `WrapError`, `UnwrapError`, and `(*wrappedError).Error`.

Control flow stores the probe error in a private `wrappedError` struct; `UnwrapError` type-switches on `*wrappedError` and returns the inner value plus a boolean; `Error` delegates to the probe error's `String`. State is a single pointer. Dependencies are only the local `Error` type. Integration points are APIs that must return `error` while preserving rich probe traces for callers that know how to unwrap. Risks include wrapping nil probe errors, no support for Go's conventional `Unwrap() error`, and type identity being private. Tests cover basic unwrap success.
