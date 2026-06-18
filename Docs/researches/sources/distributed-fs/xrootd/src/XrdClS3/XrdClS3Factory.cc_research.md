# sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3Factory.cc

## Purpose

This file implements the S3 XRootD plugin factory and the shared S3 URL/signing utilities. It initializes S3 configuration from XRootD environment keys, creates S3 file/filesystem plugin objects, converts `s3://` URLs to HTTPS endpoints, loads and caches bucket credentials, and generates AWS Signature V4 authorization headers.

## Important APIs, types, and functions

The factory exports `XrdClGetPlugIn` and implements `CreateFile`/`CreateFileSystem`. `InitS3Config` reads defaults and environment imports for endpoint, URL style, region, mkdir sentinel, default credential file locations, and per-bucket credential configs. `GenerateHttpUrl` maps S3 URLs into path-style or virtual-hosted-style HTTPS URLs and strips internal `authz` query parameters via `CleanObjectName`. `ExtractHostname`, `GetBucketFromHttpsUrl`, `PathEncode`, `CanonicalizeQueryString`, `TrimView`, and local `AmazonURLEncode` support URL canonicalization.

`GenerateV4Signature` loads credentials with `GetCredentialsForBucket`, adds required `Host`, `X-Amz-Date`, and `X-Amz-Content-Sha256` headers, builds canonical request and string-to-sign, derives the AWS4 HMAC key chain using OpenSSL HMAC/SHA256, and returns the `Authorization` header value. `ReadShortFile` and `FullRead` read credential files up to 32 KiB. Static testing/config setters live in the header.

## Control flow

The constructor runs initialization once, obtains the default log/env, sets topic name, and marks the factory initialized. File/filesystem creation returns null if initialization failed. Header callouts in S3 file/filesystem code call `GenerateV4Signature` for each HTTP request. If credentials are missing or configured as public, the auth token is empty and no signing is needed. Credential reads are cached per bucket for one minute on success/public access and ten seconds on failures.

URL generation handles several modes: if no global endpoint is configured or the URL bucket matches the endpoint, the endpoint is taken from the URL authority and the real bucket is parsed from the path; otherwise endpoint/region/url-style settings determine the HTTPS authority and path.

## State and persistence behavior

Static process-wide state includes initialization flags, log pointer, endpoint/service/region/url-style, mkdir sentinel, default credential locations, per-bucket credential locations, and a credential-value cache protected by `m_bucket_auth_map_mutex`. Secrets are read from files and kept in memory briefly. Nothing is persisted by this code.

## Dependencies and integration points

The file depends on OpenSSL EVP/HMAC for SHA256/HMAC, XRootD plugin factory/log/env APIs, POSIX file reads, and S3 file/filesystem classes. It integrates with the HTTP plugin through S3 header callouts that add SigV4 headers to HTTP operations.

## Risks and edge cases

SigV4 canonicalization is security-sensitive. The code computes `value_trimmed` and compresses spaces but then stores the original `value` in `transformed_headers`, so canonical headers may not use the normalized value intended by the comments. Query canonicalization skips empty values in some paths, which may differ from AWS rules for empty-valued parameters. Virtual-host URL generation with an empty region constructs `bucket..endpoint`. Credential cache entries store secret material in memory and use short TTLs but no explicit zeroization. `TrimView` can index an empty view if called with all whitespace because it uses the original input size while indexing the trimmed view.

## Test signals

High-value tests should cover path and virtual URL generation, endpoint-in-URL mode, `authz` stripping while preserving other query parameters, bucket extraction, path/query canonicalization, public buckets, missing/mismatched credential files, credential cache TTL and reset, SigV4 known test vectors, header normalization, empty/all-whitespace trim inputs, and plugin initialization without env/log. No dedicated S3 factory tests were found.
