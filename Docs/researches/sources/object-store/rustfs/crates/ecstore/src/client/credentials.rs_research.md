# sources/object-store/rustfs/crates/ecstore/src/client/credentials.rs

## Purpose
Provides credential value/provider abstractions for the transition client, including static credentials, signer type selection, anonymous fallback, and STS XML error decoding helpers.

## Important APIs, types, and functions
`SignatureType` enumerates default, V4, V2, V4 streaming, and anonymous signing. `Credentials<P>` caches a `Value` from a `Provider`. `Value` holds access key, secret key, session token, expiration, and signer type. `Static` implements `Provider`. `STSError`, `ErrorResponse`, `xml_decoder`, and `xml_decode_and_body` support STS-style XML errors.

## Control flow
`Credentials::new` forces an initial refresh. `get_with_context` retrieves new credentials only when `force_refresh` or provider expiration says so, then caches the value. `Static::retrieve` returns anonymous credentials if access key or secret is empty. XML helpers convert bytes to UTF-8 and parse with quick-xml.

## State and persistence behavior
Credential cache state lives in the `Credentials` struct and is protected by `TransitionClient`'s mutex when used by HTTP request construction. Nothing is persisted to disk.

## Dependencies and integration points
The module is used by `TransitionClient`, bucket-location signing, and tests that construct static V4 clients. It depends on `time::OffsetDateTime`, `quick_xml`, serde deserialization, and standard IO error mapping.

## Risks and edge cases
`Provider::retrieve_with_cred_context` returns `Value` directly, so provider retrieval cannot report errors. `Value.expiration` is not checked by `Credentials`; expiration is delegated completely to the provider. `Static` treats either missing key component as anonymous, which can silently disable signing for partially configured credentials.

## Test signals
No local tests are present. Indirect tests create static credentials for signed HTTP requests. Useful direct tests would cover anonymous fallback, forced refresh, provider expiration, context propagation, and XML error decoding.
