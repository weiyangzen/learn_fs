## sources/distributed-fs/tahoe-lafs/src/allmydata/introducer/common.py

### Purpose
This module contains shared introducer announcement utilities and status descriptor types. It extracts Foolscap tub IDs, serializes/signs announcement dictionaries, verifies/splits signed Foolscap announcement tuples, and provides descriptor objects for introducer status pages.

### Important APIs, Types, and Functions
`get_tubid_string_from_ann` picks `anonymous-storage-FURL` or `FURL` from an announcement and delegates to `get_tubid_string`, which extracts the lower-cased tub ID from a `pb://...@...` Foolscap FURL. `sign_to_foolscap` JSON-serializes an announcement as UTF-8 bytes, signs it with Ed25519, base32-encodes the signature with a `v0-` prefix, strips the `pub-` prefix from the verifying key string, and returns `(msg, sig, key)`. `unsign_from_foolscap` validates the `v0-` prefixes, rebuilds the public verifying key, verifies the signature, JSON-decodes the message, and returns `(announcement, key_vs)`. `UnknownKeyError` distinguishes unsupported unsigned/unknown-key formats. `SubscriberDescriptor` and `AnnouncementDescriptor` are plain status containers.

### Control Flow
Signing is deterministic for the JSON bytes produced by `jsonbytes.dumps`, aside from the signing key. Verification rejects missing signature/key data, unknown version prefixes, bad base32/key material, or signature mismatch before JSON decoding is returned to callers. `AnnouncementDescriptor` decodes connection hints from `anonymous-storage-FURL` using Foolscap `decode_furl` when present.

### State and Persistence Behavior
No persistent state is stored here. The signed tuple returned by `sign_to_foolscap` is the durable/wire representation stored by client caches and server announcement maps. Descriptor instances hold snapshot attributes for status displays.

### Dependencies and Integration Points
The module depends on Foolscap FURL decoding, Tahoe Ed25519 utilities, Tahoe `base32`, JSON byte utilities, and `remove_prefix`. It is used by both `introducer/client.py` and `introducer/server.py`, and the descriptor classes are returned from `IntroducerService.get_announcements()` and `get_subscribers()` for web/status code.

### Risks and Edge Cases
`get_tubid_string` asserts the FURL regex matches, so malformed FURLs fail hard. The signature version is fixed to `v0-`; future versioning needs explicit compatibility logic. The claimed key is trusted only after signature verification, but callers must handle `BadSignature` and `UnknownKeyError`. JSON byte/text normalization is part of cross-version compatibility and can be sensitive to non-ASCII or non-JSON-serializable announcement fields.

### Test Signals
`test_introducer.py::Signatures` checks signing round trips, byte types, prefix validation, missing signature/key rejection, bad signature rejection, and unknown version rejection. Additional introducer tests exercise descriptor/status paths through server announcement and subscription state.
