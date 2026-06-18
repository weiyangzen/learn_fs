# sources/object-store/rustfs/crates/ecstore/src/client/bucket_cache.rs

## Purpose
Maintains an in-memory bucket-to-region cache and implements bucket location discovery for the transition client.

## Important APIs, types, and functions
`BucketLocationCache::new/get/set/delete` wraps a `HashMap<String, String>`. `TransitionClient::get_bucket_location`, `get_bucket_location_inner`, and `get_bucket_location_request` perform cached region lookup. `process_bucket_location_response` maps S3 location XML and several error responses to region strings.

## Control flow
If the client has an explicit region, lookup returns it immediately. Otherwise it checks the cache, signs and sends `GET ?location`, reads the response, parses either `LocationConstraint` or Huawei-style `CreateBucketConfiguration`, normalizes empty location to `us-east-1` and `EU` to `eu-west-1`, then caches the result.

## State and persistence behavior
State is a process-local `HashMap` protected by the `TransitionClient` mutex. It is invalidated by bucket deletion code and updated on successful/derived location lookup. No disk persistence exists.

## Dependencies and integration points
It depends on transition-client credentials/signing, `UNSIGNED_PAYLOAD`, error parsing, `rustfs_signer`, quick-xml, and S3 error code semantics. Request construction reuses the client's path-vs-virtual-host decision and user-agent helper.

## Risks and edge cases
Region signing is hard-coded to `us-east-1` for location requests. Virtual-host URL construction omits explicit port in the virtual-style branch. Some error cases convert `AccessDenied` or authorization-region errors into location guesses, which is useful for AWS-compatible behavior but may mask policy failures. The cache has no TTL.

## Test signals
No local tests are present. Important tests would cover cache hit/miss, EU/empty normalization, Huawei XML shape, NotImplemented special cases, AccessDenied region extraction, and signed request headers for V2/V4/anonymous credentials.
