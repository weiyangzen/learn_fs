# sources/security-integrity/selinux/libsepol/src/ibpkey_record.c

Purpose: implements high-level `sepol_ibpkey_t` and `sepol_ibpkey_key_t` records for InfiniBand partition-key context entries, keyed by subnet prefix and pkey range.

Important APIs and functions: key APIs are `sepol_ibpkey_key_create`, `sepol_ibpkey_key_unpack`, `sepol_ibpkey_key_extract`, and `sepol_ibpkey_key_free`. Record APIs include create, clone, free, compare functions, low/high getters, single pkey and range setters, subnet-prefix string and byte getters/setters, and context get/set. Internal helpers parse/format subnet prefixes with `inet_pton`/`inet_ntop` and allocate string buffers.

Control flow: string subnet prefixes are parsed as IPv6 addresses and the first 64 bits are copied into a `uint64_t`. Formatting builds an IPv6 address with the stored prefix in the leading bytes. Creation initializes prefix/range to zero; setters update numeric fields; context assignment clones the supplied context. Key extraction formats then reparses the subnet prefix through the public key constructor.

State and persistence behavior: records and keys are heap-owned caller objects. Contexts are deep-cloned. No policydb mutation occurs here.

Dependencies and integration points: uses networking address conversion, public pkey headers, internal context cloning, and debug logging. `ibpkeys.c` converts these records to `OCON_IBPKEY` entries, while kernel-to-CIL writes them as `ibpkeycon`.

Risks: subnet prefix byte ordering is subtle because bytes are copied directly between `struct in6_addr` and `uint64_t`; cross-platform endianness assumptions must match policydb storage. Range setters do not validate low <= high; validation happens in `ibpkeys.c`. Error message formatting has minor missing spacing but no functional effect.

Test signals: parse/format subnet prefixes, byte getter/setter round trips, invalid IPv6 strings, low/high and single-pkey setters, range ordering deferred validation, compare ordering by prefix/low/high, clone independence, and context deep-copy behavior.
