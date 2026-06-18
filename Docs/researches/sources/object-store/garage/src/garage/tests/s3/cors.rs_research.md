# sources/object-store/garage/src/garage/tests/s3/cors.rs

Purpose: This test verifies direct S3 API CORS behavior, specifically that Garage reflects the request origin when multiple origins are configured rather than returning the wrong allowed origin.

Important APIs and types: Helpers `send_preflight`, `send_put`, and `apply_bucket_cors` use `CustomRequester`, AWS SDK `CorsConfiguration`/`CorsRule`, Hyper `Method`/`StatusCode`, and fixed origin/header constants.

Control flow: The test creates a bucket, applies CORS allowing one origin, sends an OPTIONS preflight and a signed PUT with that origin, and checks `access-control-allow-origin`. It then updates CORS to allow two origins and repeats the preflight and PUT for the first origin.

State and persistence behavior: It persists bucket CORS configuration and writes the probe object on PUT. The relevant state is the response header chosen from configured allowed origins and request origin.

Dependencies and integration points: It ties S3 bucket CORS configuration, custom signed requests, preflight request handling, object PUT, and response header generation.

Risks: The test only covers PUT and a fixed set of request headers. It does not test wildcard origins, disallowed origins, deletion, max-age, or S3 SDK CORS requests.

Test signals: 200 OK responses and exact `access-control-allow-origin` equal to the request origin before and after adding a second allowed origin.
