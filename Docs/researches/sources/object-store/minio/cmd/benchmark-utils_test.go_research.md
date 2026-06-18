# sources/object-store/minio/cmd/benchmark-utils_test.go

This test utility file defines shared benchmark helpers for object-layer write paths. It benchmarks `ObjectLayer.PutObject`, multipart `PutObjectPart`, backend setup for different instance types, parallel put-object workloads, and random test payload generation.

`runPutObjectBenchmark` creates a random bucket, generates repeated-byte data of the requested size, computes MD5, and repeatedly writes distinct object names through `obj.PutObject` using `mustGetPutObjReader`. It validates returned ETags against the expected MD5. `runPutObjectPartBenchmark` creates a multipart upload for a 128 MiB object and loops through parts sized by the benchmark argument, putting each part and checking part ETags.

`benchmarkPutObjectPart`, `benchmarkPutObject`, and `benchmarkPutObjectParallel` prepare temporary test backends with `prepareTestBackend`, clean roots with `removeRoots`, and dispatch to the core benchmark routines. `runPutObjectBenchmarkParallel` uses `b.RunParallel` to write objects concurrently into a single bucket. `getRandomByte` seeds `math/rand` with `UTCNow().UnixNano()` and returns one alphabetic byte; `generateBytesData` repeats that byte to the target size.

State is temporary: buckets, uploads, and backend roots are created during benchmark execution and removed by deferred cleanup. Dependencies include `ObjectLayer`, object reader helpers, hashing helpers, random bucket/object helpers, `go-humanize`, and Go benchmark APIs.

Risks include benchmark-only code using deprecated global `rand.Seed`, possible object-name collisions in the parallel helper because each goroutine starts its local counter at zero, and an apparent off-by-one slice for non-final multipart parts (`(j+1)*partSize-1`) that benchmarks a part one byte short. These helpers are performance signals, not correctness tests, but they can expose allocation and ETag regressions in object write paths.
