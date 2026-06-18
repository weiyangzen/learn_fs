# sources/object-store/garage/src/api/s3/lifecycle.rs

## Purpose
Implements S3 bucket lifecycle configuration get, put, and delete endpoints. It persists lifecycle rules in bucket parameters and converts between Garage and S3 XML representations.

## Important APIs, Types, And Functions
`handle_get_lifecycle` reads stored lifecycle config and serializes `LifecycleConfiguration`. `handle_put_lifecycle` deserializes request XML, validates and converts it into Garage's lifecycle config, then stores it. `handle_delete_lifecycle` clears the config.

## Control Flow
GET returns `NoSuchLifecycleConfiguration` when no lifecycle config exists. PUT collects the request body, deserializes with `quick_xml`, calls `validate_into_garage_lifecycle_config`, rejects invalid rules as bad request, updates `bucket_params.lifecycle_config`, and writes the bucket. DELETE updates the same CRDT field to `None`.

## State And Persistence
State is `bucket_params.lifecycle_config` persisted by reinserting `Bucket::present(bucket_id, bucket_params)` into `bucket_table`. This file only manages configuration; lifecycle execution/expiration is elsewhere.

## Dependencies And Integration Points
Depends on shared XML lifecycle types in `garage_api_common::xml::lifecycle`, Garage bucket table persistence, and `ReqCtx`. It is dispatched by the S3 router and requires owner authorization according to router policy.

## Risks And Test Signals
Risks are validation completeness and compatibility with AWS lifecycle XML. No local tests exist in this file. Because lifecycle rules can delete or transition data elsewhere, accepting a malformed config would have broad downstream effects, so shared validation is the key dependency.
