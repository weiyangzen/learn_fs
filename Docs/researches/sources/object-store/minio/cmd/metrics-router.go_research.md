# sources/object-store/minio/cmd/metrics-router.go

Purpose: This file registers MinIO Prometheus metrics HTTP routes and selects whether those routes require JWT authentication or are public.

Important APIs and types: Constants define legacy, v2 cluster/bucket/node/resource, and v3 metrics paths, plus environment variables `MINIO_PROMETHEUS_AUTH_TYPE` and `MINIO_PROMETHEUS_OPEN_METRICS`. `prometheusAuthType` supports `jwt` and `public`. The main API is `registerMetricsRouter`.

Control flow: `registerMetricsRouter` creates a subrouter under the reserved MinIO bucket path, reads `MINIO_PROMETHEUS_AUTH_TYPE` through `env.Get`, lowercases it, and chooses `AuthMiddleware` by default or `NoAuthMiddleware` for `public`. It then registers legacy, v2 cluster, v2 bucket, v2 node, and v2 resource handlers. Finally it creates the v3 metrics server with the same auth middleware and registers `GET /metrics/v3{pathComps:.*}`, including support for query behavior implemented by that server.

State and persistence behavior: No persistent state is written. Runtime state is limited to route registration and environment-based auth choice during server setup.

Dependencies and integration points: It depends on `github.com/minio/mux`, `github.com/minio/pkg/v3/env`, MinIO auth middlewares, v2 metrics handlers, `metricsResourceHandler`, and `newMetricsV3Server`. It is part of the server router initialization path.

Risks: Setting auth type to `public` exposes metrics without JWT, which is operationally intentional but security-sensitive. Unknown auth values silently fall back to JWT. The declared `MINIO_PROMETHEUS_OPEN_METRICS` constant is not used in this file. Route ordering and reserved bucket prefix must remain consistent with other API routers.

Test signals: No direct tests are present in this subset. Integration signals should verify route availability, default JWT protection, public mode behavior, v2 resource handler registration, and v3 wildcard path handling.
