# sources/security-integrity/selinux/libsepol/include/sepol/ibpkey_record.h

Purpose: Declares the public record/key API for InfiniBand partition key ranges.

Important APIs and types: Opaque `sepol_ibpkey_t` and key type; key creation from subnet prefix plus low/high pkey, compare helpers, range setters/getters, subnet prefix string/byte accessors, context accessors, create/clone/free.

Control flow: Callers build a range identity, attach a context, and pass it to collection operations in `ibpkeys.h`.

State and persistence: Records store a subnet prefix, pkey range, and context. Persistence happens only when modifying a policydb.

Dependencies and integration points: Uses `stdint.h`, context records, and handles; maps to `OCON_IBPKEY` policydb entries.

Risks: String subnet prefix parsing and byte-order representation must be consistent with binary policy and kernel expectations. Range bounds need validation.

Test signals: String/byte prefix round trips, low/high range handling, and query/modify in policydb are key tests.
