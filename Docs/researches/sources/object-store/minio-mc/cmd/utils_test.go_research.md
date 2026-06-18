## sources/object-store/minio-mc/cmd/utils_test.go

Purpose: unit tests for `parseAttribute` in `utils.go`, focused on metadata strings stored in `X-Amz-Meta-Mc-Attrs` or the s3cmd-compatible metadata key.

Control flow uses table-driven cases for empty strings, whitespace, slash-only input, incomplete `atime:/`, key-only attributes, key-colon attributes, and a valid multi-attribute string. It asserts both returned maps and exact sentinel error identity with `ErrInvalidFileSystemAttribute`. State is local to the test. Dependencies are Go `testing` and `reflect.DeepEqual`. The test signal is useful but narrow: it does not cover `parseAtimeMtime`, alternate metadata keys, duplicate attributes, or malformed colon counts beyond the listed cases. Risk is exact error comparison, which depends on returning the package sentinel.
