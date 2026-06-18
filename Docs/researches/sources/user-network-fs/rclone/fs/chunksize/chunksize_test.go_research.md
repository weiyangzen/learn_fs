# sources/user-network-fs/rclone/fs/chunksize/chunksize_test.go

Purpose: validates `chunksize.Calculator` over representative multipart upload sizing cases.

Important APIs/functions: `TestComputeChunkSize` is table-driven and uses `toSizeSuffixMiB` for expected MiB values.

Control flow: each case calls `Calculator`, compares the returned chunk size, and for known-size inputs verifies the returned size yields at most `maxParts`. When the returned size is larger than the default, it also verifies one MiB less would exceed the part limit, proving the result is minimal under the MiB rounding rule.

State and persistence behavior: no state. Test names document expected behavior for streaming files, exact divisibility, one-byte overflow, and real-world issue sizing.

Dependencies and integration points: depends on `fs.SizeSuffix` and `fs.Mebi`. It protects upload behavior for backends using the shared calculator.

Risks: no tests cover invalid `maxParts` values or zero/negative default chunk sizes, which are caller preconditions.

Test signals: strong deterministic coverage for arithmetic edge cases and minimality.
