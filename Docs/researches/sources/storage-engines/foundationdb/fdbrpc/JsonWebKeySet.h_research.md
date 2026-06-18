# sources/storage-engines/foundationdb/fdbrpc/JsonWebKeySet.h

`JsonWebKeySet.h` declares the restricted JWKS model used by fdbrpc authorization and key loading.

`PublicOrPrivateKey` wraps either `PublicKey` or `PrivateKey` in a `std::variant` and provides type predicates plus getters. `JsonWebKeySet` stores a `std::map<Standalone<StringRef>, PublicOrPrivateKey>` and declares `parse(StringRef jwksString, VectorRef<StringRef> allowedUses)` plus `toStringRef(Arena&)`.

The header defines API shape only; implementation in `JsonWebKeySet.cpp` validates JSON, algorithm/type constraints, optional use values, and supported key parameters. Serialized output is written into a caller-provided arena.

State is an in-memory key map with standalone string key IDs. Dependencies are Flow `Arena`, `PKey`, `StringRef`, STL `map`, and `variant`. Consumers include `JsonWebKeySet.cpp` and `FlowTransport.cpp`.

Risks include wrong getter usage on the active variant, which throws `std::bad_variant_access`, and caller assumptions beyond the documented restricted key support. Tests in the `.cpp` file exercise parse/serialize for supported EC and RSA key types.
