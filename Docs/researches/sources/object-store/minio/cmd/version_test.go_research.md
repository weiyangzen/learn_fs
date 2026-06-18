# sources/object-store/minio/cmd/version_test.go

Simple smoke test that assigns `Version` to an RFC3339 timestamp and verifies `time.Parse(time.RFC3339, Version)` succeeds.

It mutates package global `Version` without restoration. The test checks only timestamp shape, not build-time injection, release tag conversion, or update integration.
