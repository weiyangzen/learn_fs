# sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3Factory.hh

## Purpose
Declares the `XrdClS3::Factory` plugin factory for mapping `s3://` client URLs onto the XRootD HTTP client plugin. It centralizes S3 URL translation, AWS V4 request signing, endpoint/region/service configuration, bucket credential lookup, and test/configuration setters.

## Important APIs, Types, and Functions
`Factory` derives from `XrdCl::PlugInFactory` and overrides `CreateFile()` and `CreateFileSystem()`. Static helpers include `GenerateHttpUrl()`, `GenerateV4Signature()`, `GetBucketFromHttpsUrl()`, `GetCredentialsForBucket()`, `PathEncode()`, `CanonicalizeQueryString()`, `CleanObjectName()`, `ExtractHostname()`, and `TrimView()`. The private `Credentials` struct stores access/secret key material.

## Control Flow
The factory is the entry point used by XrdCl plugin loading. File and filesystem wrappers call its static helpers on every S3 operation: first to translate a logical S3 URL into an HTTPS URL, then from HTTP header callouts to produce per-request authorization headers.

## State and Persistence Behavior
Configuration is static process state: endpoint, service, region, URL style, mkdir sentinel, default credentials, per-bucket credentials, and a bucket credential cache with timestamps. `m_init_once` guards initialization; `m_bucket_auth_map_mutex` protects cached credential reads/writes. There is no file persistence here, but credentials may be sourced from XRootD client configuration in the implementation.

## Dependencies and Integration Points
Depends on `XrdCl::PlugInFactory`, `XrdCl::FilePlugIn`, `XrdCl::FileSystemPlugIn`, `XrdCl::Log`, STL strings, maps, tuples, chrono, mutexes, and shared mutexes. It integrates with `XrdClS3File`, `XrdClS3Filesystem`, and the `XrdClHttpHeaderCallout` property used by the HTTP plugin.

## Risks and Edge Cases
Static setters and credential maps can affect all plugin instances in-process. V4 signing is sensitive to canonical path/query/header ordering and exact bucket extraction. Credential cache invalidation, per-bucket override precedence, and query cleaning are security-relevant. `SetBucketCredentials()` mutates `m_bucket_location_map` without the same visible lock used for the auth cache.

## Test Signals
Unit tests should cover virtual-hosted and path-style URL generation, bucket extraction, query canonicalization, object-name cleaning, path encoding, whitespace trimming, credential precedence/cache reset, and V4 signing against known AWS examples. Integration tests should verify signed HTTP requests through `XrdClS3::File` and `Filesystem`.
