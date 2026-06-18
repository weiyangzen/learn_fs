# sources/object-store/rustfs/crates/e2e_test/src/bucket_logging_test.rs

## Purpose
This file tests S3-compatible "dummy" bucket control APIs: bucket logging, accelerate configuration, request payment, and website configuration. It verifies both AWS SDK behavior and raw HTTP/XML contracts.

## Important APIs, Types, and Functions
Helpers locate and invoke `awscurl`, parse HTTP status lines, extract bodies, and extract headers from raw output. Tests use AWS SDK types such as `BucketLoggingStatus`, `LoggingEnabled`, `AccelerateConfiguration`, `BucketAccelerateStatus`, `RequestPaymentConfiguration`, `Payer`, `WebsiteConfiguration`, and `IndexDocument`.

## Control Flow
The main existing-bucket test creates a bucket, checks default logging, persists logging, checks default accelerate and request-payment settings, writes accelerate and request-payment settings, writes website config, verifies website config, deletes it, and checks the expected missing-config error. The missing-bucket test calls every relevant get/put/delete path and expects `NoSuchBucket`. The HTTP-contract test uses awscurl to assert raw status codes and XML bodies for query-string APIs.

## State and Persistence
The tests persist bucket-level subresource configuration in the temporary RustFS server: logging target/prefix, accelerate status, request payer, and website config. Website config deletion is verified.

## Dependencies and Integration Points
The suite integrates AWS SDK S3 subresource APIs, raw SigV4 HTTP requests via awscurl, XML response formatting, and RustFS bucket metadata persistence. It uses `RustFSTestEnvironment` for lifecycle.

## Risks and Edge Cases
The HTTP-contract test is skipped if awscurl is unavailable, leaving only SDK-level coverage. These are compatibility endpoints and may not implement full AWS semantics beyond dummy/default behavior. Fixed bucket names require serial execution.

## Test Signals
Signals include default empty logging, persisted logging target/prefix, default `BucketOwner` payer, persisted `Requester`, default empty accelerate status, persisted `Suspended`, `NoSuchWebsiteConfiguration` after website deletion, `NoSuchBucket` for missing buckets, HTTP 200/204/404 status contracts, and XML content checks.
