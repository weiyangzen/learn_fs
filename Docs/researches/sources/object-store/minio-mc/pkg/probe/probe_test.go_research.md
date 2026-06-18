## sources/object-store/minio-mc/pkg/probe/probe_test.go

Purpose: gocheck tests for probe tracing and error wrapping.

Control flow defines three helper functions that stat a non-existent file and add trace tags, calls `probe.Init`, sets `Commit-ID`, verifies traced errors are non-nil, adds another trace, then verifies `WrapError`/`UnwrapError` round-trips a `*probe.Error`. State is global probe root/app info and local error values. Dependencies are `os`, `testing`, probe, and gocheck. Test signal confirms happy-path construction but does not assert trace contents, string formatting, system info, `Untrace`, nil behavior, or concurrent access. It is a smoke test rather than a full specification.
