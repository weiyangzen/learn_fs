# sources/user-network-fs/blobfuse2/component/azstorage/policies.go

Purpose: `policies.go` defines custom Azure SDK pipeline policies used by BlobFuse2 storage clients: a telemetry policy, a service API version override policy, and a rate-limiting policy for operations and download bandwidth.

Important APIs, types, and functions: `blobfuseTelemetryPolicy` and `newBlobfuseTelemetryPolicy` prepend BlobFuse2 telemetry to the request `User-Agent`. `serviceVersionPolicy` and `newServiceVersionPolicy` overwrite the `x-ms-version` header. `rateLimitingPolicy` and `newRateLimitingPolicy` create `golang.org/x/time/rate` limiters for read bytes per second and operations per second. `(*rateLimitingPolicy).Do` waits on the ops limiter for every request and waits on the bandwidth limiter only for `GET` requests with a `x-ms-range` or `Range` header parsed by `parseRangeHeader`.

Control flow: Each policy implements `policy.Policy.Do`, mutates or throttles the request, and then calls `req.Next()`. The rate-limiter constructor builds 10-second burst windows and clamps burst sizes to `math.MaxInt` to avoid overflow on small `int` platforms. On request execution, ops limiting occurs first. Bandwidth limiting then inspects range headers for GET downloads and waits for exactly the requested byte count before forwarding the request.

State and persistence behavior: Policies hold in-memory limiter state only. Token buckets persist across requests that share the same client pipeline. No storage state is modified directly, but throttling changes request timing and cancellation behavior because waits use the request context.

Dependencies and integration points: The file depends on Azure SDK `policy`, Go `net/http`, `x/time/rate`, BlobFuse2 `common` headers/logging, and `parseRangeHeader` plus `X_Ms_Range`/`RangeHeader` constants from `utils.go`. `getAzStorageClientOptions` installs telemetry and optional service-version policies as per-call policies and installs rate limiting as a per-retry policy when configured.

Risks: Invalid range headers cause the policy to fail the request before it reaches storage. Bandwidth limiting is skipped for GET requests without range headers, so callers using full-object GETs are not throttled by bytes. The lower-case `x-ms-range` map lookup is intentional for SDK behavior but sensitive to header canonicalization changes. Per-retry placement means retries consume limiter tokens too. Very high configured rates are clamped only at burst size; token limits can still represent extreme values.

Test signals: `policies_test.go` verifies ops delays, range-based bandwidth delays for both `Range` and lower-case `x-ms-range`, no-limit fast path, and skip behavior for non-GET methods. There are no direct tests here for telemetry header concatenation, service version override, context cancellation, malformed range policy errors, or burst clamping.
