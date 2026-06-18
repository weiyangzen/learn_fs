## sources/object-store/garage/src/api/s3/api_server.rs

Purpose: wires the S3-compatible API into the shared generic server, including endpoint parsing, host bucket resolution, SigV4 auth, bucket authorization, CORS, and dispatch to S3 operation modules.

Important APIs/types/functions: `S3ApiServer`, `S3ApiEndpoint`, `S3ApiServer::run`, `handle_request_without_bucket`, `ApiHandler for S3ApiServer`, and `ApiEndpoint for S3ApiEndpoint`.

Control flow: `parse_endpoint` requires Host, normalizes authority to host, extracts virtual-host bucket from configured root domain, and delegates to S3 router. `handle` processes `PostObject` and `Options` before SigV4. Authenticated requests are verified with service `s3`; bucketless requests only support `ListBuckets`; `CreateBucket` has a special path before bucket resolution. Other requests resolve bucket for the key, check endpoint authorization against key permissions, find matching CORS, build `ReqCtx`, dispatch across object, multipart, bucket, CORS, lifecycle, and website handlers, then applies CORS to successful responses.

State/persistence: reads key/bucket config and delegates object/bucket mutations to handler modules. No local durable state.

Dependencies/integration: integrates most S3 handler modules, common server/auth/CORS/helpers, Garage model key table, and route endpoint metadata.

Risks: early `PostObject` bypasses standard `verify_request` path and must perform its own auth. `bucket_name.unwrap()` for PostObject assumes router always supplies a bucket. Permission classification in the router is security-critical. Only implemented endpoints are dispatched; unknown supported-looking endpoints return `NotImplemented`.

Test signals: no local tests; S3 integration tests should cover host parsing, auth, bucket permissions, preflight, list pagination, multipart, lifecycle/CORS/website, and unimplemented paths.
