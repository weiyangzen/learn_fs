# sources/storage-engines/foundationdb/fdbrpc/JsonWebKeySet.cpp

`JsonWebKeySet.cpp` parses and writes FoundationDB's restricted JSON Web Key Set format for public/private key handling.

The implementation reads required/optional JWK string members, decodes base64url big-number fields, parses ES256/P-256 EC keys, parses RS256 RSA keys, dispatches by `kty`, and serializes supported `PublicKey`/`PrivateKey` values back to JWKS. Public entry points are `JsonWebKeySet::parse()` and `JsonWebKeySet::toStringRef()`. The code has distinct OpenSSL 3 provider API and older OpenSSL/BoringSSL paths.

Parsing requires a top-level object with a `keys` array. Each key must be an object with unique `kid`, supported `kty`, matching `alg`, and required parameters. Optional `use` is checked when allowed uses are supplied. RSA private keys must provide all six CRT private members or none. Serialization walks the key map, extracts OpenSSL parameters, base64url-encodes them, and writes a JWKS object.

State is in-memory in a `JsonWebKeySet::KeyMap`; temporary data uses `Arena` and `AutoCPointer` for OpenSSL ownership. Disk I/O is handled elsewhere by `FlowTransport`. Dependencies include Flow `Arena`, `PKey`, `MkCert`, base64 helpers, RapidJSON, and OpenSSL EC/RSA/EVP APIs.

Risks include narrow algorithm support, duplicate-key rejection, OpenSSL portability differences, sensitive private-key handling, and suppressed repeated parse/write logs. Tests round-trip EC/RSA public/private generated keys and verify signatures, plus an empty key-set parse.
