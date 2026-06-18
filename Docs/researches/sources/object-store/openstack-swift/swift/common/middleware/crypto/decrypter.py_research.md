# sources/object-store/openstack-swift/swift/common/middleware/crypto/decrypter.py

## Purpose
`decrypter.py` restores encrypted Swift object responses and encrypted container-listing ETags to client-visible plaintext. It handles object GET/HEAD metadata and body decryption, ranged and multipart byte-range responses, and JSON container listings.

## Important APIs, Types, and Functions
`purge_crypto_sysmeta_headers()` strips crypto private headers. `BaseDecrypterContext` provides crypto metadata extraction, wrapped-key unwrapping, encrypted-header decryption, and key retrieval. `DecrypterObjContext` handles object responses with `decrypt_resp_headers()`, `response_iter()`, and `multipart_response_iter()`. `DecrypterContContext` decrypts JSON listing hashes. `Decrypter` routes supported requests.

## Control Flow
For valid Swift container/object paths, `Decrypter` handles object GET/HEAD and container GET. Object handling calls the downstream app, reads body and metadata crypto headers, fetches keys using stored key ids, decrypts encrypted ETag and user metadata headers, purges crypto sysmeta, optionally exposes backend crypto cipher, and decrypts body streams for successful GETs. Range responses compute the correct AES-CTR offset from `Content-Range`; multipart byteranges decrypt each part from its first byte. Container GET JSON bodies are fully read, parsed, and each object `hash` with appended crypto meta is decrypted using the container key.

## State and Persistence
No local state is persisted. It consumes persistent crypto metadata stored in object sysmeta/transient sysmeta and container listing hash values. Container listing responses are materialized in memory to update JSON and content length.

## Dependencies and Integration Points
It depends on `CryptoWSGIContext`, crypto metadata utilities, Swift header helpers, `HeaderKeyDict`, content-range/type parsers, multipart byterange parsing, and keymaster callbacks. It is composed outside `Encrypter` by the crypto package factory.

## Risks and Edge Cases
Malformed or missing required crypto metadata yields 500s for object decrypts. Unknown secret ids in container listings are masked as `<unknown>` after logging, preserving listability but losing exact ETag. JSON listings are fully buffered, so very large listings have memory implications. Multipart decryption must preserve MIME framing exactly. Override mode skips decryption entirely.

## Test Signals
Tests should cover encrypted ETag restoration, user metadata restoration, CORS exposed-header updates, body decryption for full and ranged GETs, multipart byteranges, HEAD without body decryption, crypto sysmeta purge, container JSON hash decryption, unknown secret handling, malformed metadata 500s, override bypass, invalid path/API bypass, and content-length recalculation for listings.
