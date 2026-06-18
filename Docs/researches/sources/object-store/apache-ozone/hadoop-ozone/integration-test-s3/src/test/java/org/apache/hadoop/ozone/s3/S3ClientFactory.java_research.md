# sources/object-store/apache-ozone/hadoop-ozone/integration-test-s3/src/test/java/org/apache/hadoop/ozone/s3/S3ClientFactory.java

## Purpose

This factory creates AWS SDK v1 and v2 S3 clients configured for the mini-cluster S3 Gateway endpoint. It supports sync and async v2 clients and path-style toggles for endpoint compatibility tests.

## Important APIs, types, and functions

The class exposes `createS3Client()`, `createS3Client(boolean)`, `createS3ClientV2()`, `createS3ClientV2(boolean)`, `createS3AsyncClientV2()`, `createS3AsyncClientV2(boolean)`, and generic `configureCommon()`. It uses AWS SDK v1 `AmazonS3ClientBuilder`, `BasicAWSCredentials`, `AWSStaticCredentialsProvider`, and SDK v2 `S3ClientBuilder`, `S3AsyncClientBuilder`, `AwsBasicCredentials`, `StaticCredentialsProvider`, and `S3BaseClientBuilder`.

## Control flow, state, and persistence

The factory stores the `OzoneConfiguration`. For each client creation, it reads Hadoop HTTP policy, chooses HTTP or HTTPS S3G address keys, builds an endpoint URI, applies static test credentials `user/password`, sets a fixed region, and enables path-style access when requested. No state is persisted beyond the created client instances.

## Dependencies and integration points

The factory integrates S3 Gateway test configuration with AWS SDK clients. It depends on `S3GatewayConfigKeys` and Hadoop HTTP policy. The created clients are consumed by abstract AWS SDK integration suites outside this subset.

## Risks and test signals

HTTPS is noted as currently disabled in tests, so HTTPS client paths are lightly exercised. Static credentials must match S3G test authentication expectations. Endpoint host comes directly from configuration; if a service mutates the configuration to a proxy address, clients route through the proxy. Positive signals are SDK v1/v2 clients successfully issuing bucket/object operations with path-style addressing.
