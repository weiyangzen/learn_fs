# sources/object-store/garage/src/api/s3/website.rs

## Purpose
Implements S3 bucket website configuration get, put, and delete endpoints, and defines the `x-amz-website-redirect-location` object metadata header constant used by PUT/COPY.

## Important APIs, Types, And Functions
`X_AMZ_WEBSITE_REDIRECT_LOCATION` is the shared header name. `handle_get_website` serializes the stored Garage website config into `WebsiteConfiguration` XML. `handle_put_website` deserializes and validates XML then stores Garage website config. `handle_delete_website` clears it.

## Control Flow
GET returns an XML configuration when present. Unlike CORS/lifecycle, absence returns 204 No Content rather than an S3 missing-configuration error. PUT collects the body, deserializes with `quick_xml`, validates website config, converts it into Garage's internal representation, and writes the bucket. DELETE sets the config to `None` and writes the bucket.

## State And Persistence
State is `bucket_params.website_config`, persisted by inserting `Bucket::present(bucket_id, bucket_params)` into `bucket_table`. Object-level redirect metadata is not stored here, but the exported header constant is used by `put.rs` metadata extraction and `copy.rs` metadata-copy filtering.

## Dependencies And Integration Points
Depends on shared website XML types, Garage bucket table persistence, and `ReqCtx`. The website serving path uses this stored config together with GET/HEAD helpers to serve index/error behavior elsewhere.

## Risks And Test Signals
Risks are AWS compatibility for no-config GET behavior, validation completeness for routing rules, and consistency of redirect header semantics across PUT and COPY. No local tests are present in this file; validation is delegated to shared XML website code.
