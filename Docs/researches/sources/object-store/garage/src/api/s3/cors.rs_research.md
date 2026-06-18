# sources/object-store/garage/src/api/s3/cors.rs

## Purpose
Provides S3 bucket CORS configuration endpoints: get, put, and delete. It converts between Garage's stored CORS representation and the shared S3 XML CORS schema.

## Important APIs, Types, And Functions
`handle_get_cors` reads `bucket_params.cors_config` and serializes a `CorsConfiguration` XML document. `handle_put_cors` deserializes request XML with `quick_xml::de::from_reader`, validates it, converts it into Garage's internal CORS config, and stores it. `handle_delete_cors` clears the config.

## Control Flow
GET returns `NoSuchCORSConfiguration` when no config is present; otherwise it maps every stored rule through `CorsRule::from_garage_cors_rule`. PUT collects the whole body, deserializes and validates before mutating state, then writes a fresh `Bucket::present(bucket_id, bucket_params)` to the bucket table. DELETE updates the config CRDT to `None` and writes the bucket back.

## State And Persistence
The only persistent state is `bucket_params.cors_config`, stored through `garage.bucket_table.insert`. Updates preserve the rest of the bucket parameters by mutating the received `bucket_params` clone and reinserting a present bucket record.

## Dependencies And Integration Points
Depends on `garage_api_common::xml::cors` for XML shapes and validation, `garage_model::bucket_table::Bucket` for persistence, and `ReqCtx` for resolved bucket identity and parameters. Runtime CORS request evaluation is outside this file but consumes the same stored config.

## Risks And Test Signals
Primary risks are schema compatibility and whether `validate()` fully enforces AWS constraints. The module does not include local tests; coverage likely comes from shared XML CORS tests or integration tests. Error behavior is straightforward: missing config is an S3-specific not-found error, malformed XML becomes `MalformedXML`.
