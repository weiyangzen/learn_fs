# sources/object-store/minio/cmd/utils_test.go

Unit tests for selected `utils.go` helpers. Coverage includes S3 size/part limits, bucket/object path splitting with slash edge cases, invalid profiler type handling, local URL parsing helper, JSON request dumping and percent escaping, `ToS3ETag`, `ceilFrac`, ignored-error matching, `restQueries`, longest common prefix mode, and `getMinioMode`.

The file mutates `globalIsDistErasure` and `globalIsErasure`, builds HTTP requests, and otherwise avoids disk/network persistence.

Useful regression signals exist for core small helpers, but many shared utilities remain untested in this subset, especially checksum readers, transports, audit, profiler success paths, OpenID, and object-error mapping.
