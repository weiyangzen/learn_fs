# sources/user-network-fs/rclone/fs/chunksize/chunksize.go

Purpose: calculates the minimum upload chunk size needed to keep a file within a backend's maximum part count while avoiding unnecessary memory growth.

Important APIs/functions: `Calculator(o any, size int64, maxParts int, defaultChunkSize fs.SizeSuffix) fs.SizeSuffix`.

Control flow: for streaming/unknown size (`size < 0`), it logs the upload capacity implied by the default and returns the default. For known sizes, it computes how many default-size chunks would be needed. If the default is sufficient, including exact boundary divisibility, it returns the default. Otherwise it divides file size by `maxParts`, rounds up to the nearest MiB, and adds another MiB for boundary cases that would still produce too many parts.

State and persistence behavior: pure calculation with debug logging only. No persistent state.

Dependencies and integration points: uses `fs.SizeSuffix`, `fs.Mebi`, and `fs.Debugf`. Backends can call it when preparing multipart uploads to pick an upload chunk size from object size and service part limits.

Risks: assumes `maxParts` is positive; callers must validate that. Rounds to MiB, which is conservative but may be larger than a backend with byte-granular chunks strictly needs. The boundary condition uses modulo by `maxParts` rather than `minChunk`, matching the current test expectations but worth preserving carefully.

Test signals: `chunksize_test.go` covers streaming, default sufficiency, rounding, one-byte overflow, minimum MiB behavior, and a forum-derived large file case.
