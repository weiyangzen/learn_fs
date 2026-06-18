# sources/object-store/openstack-swift/swift/common/middleware/crypto/encrypter.py

## Purpose
`encrypter.py` encrypts new object bodies and user metadata on PUT/POST, masks conditional ETags on GET/HEAD so encrypted on-disk objects can still satisfy plaintext ETag conditions, and writes crypto metadata needed for future decryption.

## Important APIs, Types, and Functions
`encrypt_header_val()` encrypts a header value and returns ciphertext plus crypto meta. `_hmac_etag()` computes the stored plaintext ETag MAC. `EncInputWrapper` encrypts request body chunks and installs a footer callback. `EncrypterObjContext` handles object PUT, POST, and GET/HEAD. `Encrypter` routes requests and honors `disable_encryption` and `swift.crypto.override`.

## Control Flow
PUT handling validates metadata before encryption, fetches object and container keys, encrypts user metadata into transient sysmeta, wraps `wsgi.input` with `EncInputWrapper`, and calls downstream. The wrapper lazily creates a random body key, wraps it with the object key, AES-CTR encrypts chunks, computes plaintext and ciphertext MD5s, validates any client ETag against plaintext, writes ciphertext ETag plus encrypted plaintext ETag/body metadata into footers, and encrypts container-listing ETag override with the container key. POST encrypts metadata only. GET/HEAD masks `If-Match` and `If-None-Match` values by appending HMACs for all known root secrets and sets an ETag-is-at header for object-server comparison.

## State and Persistence
Per-request encryption contexts, MD5 digests, and body crypto metadata live in memory. Persistent outputs are object sysmeta/transient sysmeta headers and footer metadata: encrypted ETag, body crypto meta, body key wrap, key id, ETag MAC, encrypted user metadata, and encrypted container listing override ETag.

## Dependencies and Integration Points
It depends on `CryptoWSGIContext`, `Crypto`, Swift metadata helpers, footer callback chaining, request `InputProxy`, conditional header helpers, keymaster callbacks, and container update override headers. It must run where downstream proxy controllers support footer callbacks.

## Risks and Edge Cases
If no body bytes are read, no body crypto sysmeta is written and any client ETag is restored. Metadata length is checked before encryption, but encoded/encrypted values can still change downstream header sizes. Conditional masking must include historic keys for key rotation. Pipeline order with copy and large-object middleware is critical. AES-CTR encryption is not authenticated; ETag/MAC handling is the primary integrity signal used by Swift paths.

## Test Signals
Tests should cover PUT body encryption and footer metadata, empty-body behavior, client ETag validation failure, response ETag plaintext replacement, metadata encryption on PUT/POST, disabled encryption, crypto override, conditional ETag masking with current and historic keys, container-listing ETag override encryption, footer callback chaining, and downstream error behavior.
