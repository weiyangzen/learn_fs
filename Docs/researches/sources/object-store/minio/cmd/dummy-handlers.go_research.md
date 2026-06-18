<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/dummy-handlers.go -->
## sources/object-store/minio/cmd/dummy-handlers.go

Purpose: This file implements dummy S3-compatible bucket configuration handlers for APIs MinIO chooses not to fully support while still returning AWS-compatible responses or errors. The handlers validate authorization and bucket existence before returning fixed XML, missing-configuration errors, not-implemented errors, or success for no-op deletes.

Important APIs and functions: Methods on `objectAPIHandlers` include `GetBucketWebsiteHandler`, `GetBucketAccelerateHandler`, `GetBucketRequestPaymentHandler`, `GetBucketLoggingHandler`, `DeleteBucketWebsiteHandler`, `GetBucketCorsHandler`, `PutBucketCorsHandler`, and `DeleteBucketCorsHandler`. They use `newContext`, `logger.AuditLog`, `mux.Vars`, `api.ObjectAPI`, `checkRequestAuthType`, `GetBucketInfo`, `writeErrorResponse`, `writeSuccessResponseXML`, and `writeSuccessResponseHeadersOnly`.

Control flow: Most GET handlers share the same sequence: create request context, defer audit logging, extract bucket from route variables, reject uninitialized object API, authorize the relevant policy action, verify the bucket exists with `GetBucketInfo`, then return a fixed response. Website and CORS GETs return `ErrNoSuchWebsiteConfiguration` and `ErrNoSuchCORSConfiguration`. Accelerate, request payment, and logging GETs return static XML defaults. CORS PUT and DELETE validate auth/bucket and then return `ErrNotImplemented`. Website DELETE is a pure success-header no-op.

State and persistence behavior: These handlers do not read or write persistent configuration beyond bucket existence checks. Static XML responses are generated inline. No CORS, website, accelerate, request-payment, or logging state is stored.

Dependencies and integration points: The file depends on `net/http`, `github.com/minio/minio/internal/logger`, `github.com/minio/mux`, and `github.com/minio/pkg/v3/policy`. It integrates with S3 routing, request auth, audit logs, bucket metadata access, and S3 error serialization.

Risks: Dummy behavior must remain compatible with client expectations. Reusing `GetBucketPolicyAction` for several dummy GET APIs is deliberate but may not match a future fine-grained permission model. `DeleteBucketWebsiteHandler` does not audit, authorize, or verify bucket existence in this file, which is a notable difference from the other handlers and may rely on outer routing/middleware behavior. Static XML strings must stay valid and AWS-compatible.

Test signals: No direct tests are listed for these handlers. Coverage is likely indirect through S3 API compatibility tests, if present elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/dummy-handlers.go -->
