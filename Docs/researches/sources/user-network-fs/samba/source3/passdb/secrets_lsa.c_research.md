# sources/user-network-fs/samba/source3/passdb/secrets_lsa.c

## Purpose
`secrets_lsa.c` layers Windows LSA secret semantics on top of `secrets.tdb`. It stores current and old secret blobs, last-change timestamps, and optional security descriptors under `SECRETS/LSA/<NAME>` keys encoded as generated `lsa_secret` NDR records.

## Important APIs, types, and functions
- `lsa_secret_key(mem_ctx, secret_name)` uppercases and formats the storage key.
- `lsa_secret_get_common` fetches, NDR-decodes, scrubs the raw blob, and marks current/old secret data as sensitive in talloc.
- `lsa_secret_get` returns optional current secret, current timestamp, old secret, old timestamp, and security descriptor to callers.
- `lsa_secret_set_common` updates the old/current secret slots and timestamps, encodes the full `lsa_secret`, and stores it with `secrets_store`.
- `lsa_secret_set` loads an existing secret when present, then writes the requested current/old/security descriptor state.
- `lsa_secret_delete` verifies the secret exists before deleting the backing key.

## Control flow
Reads build the uppercased key, use `secrets_fetch`, map missing records to `NT_STATUS_OBJECT_NAME_NOT_FOUND`, decode with `ndr_pull_lsa_secret`, and expose requested fields by shallow-copying DATA_BLOB structs owned by the caller's talloc context. Writes attempt to load the previous record. If no explicit old secret is supplied, the previous current secret becomes old and keeps its prior last-change timestamp; otherwise the supplied old secret gets the current timestamp. The supplied current secret, or null current value, also receives a fresh timestamp. The resulting structure is NDR-pushed and stored back in `secrets.tdb`.

## State and persistence behavior
Persistent state is a single NDR blob per LSA secret name in `secrets.tdb`. Names are normalized to uppercase in the key. The set path preserves old-secret history automatically unless the caller overrides it. Secret data blobs are talloc-owned after decoding and marked secret for safer diagnostics/memory handling; the raw fetched blob is burned and freed.

## Dependencies and integration points
This file depends directly on `secrets.c` generic store/fetch/delete and generated NDR definitions in `ndr_secrets.h`. It is used by the Python passdb extension and any source3 code that needs LSA-style secrets rather than simple string/blob keys.

## Risks and edge cases
- Returned `DATA_BLOB`s are shallow views into the decoded `struct lsa_secret`; callers must keep the talloc context alive.
- `lsa_secret_set` treats missing existing records as creation, but propagates other decode/fetch errors; corrupt records block updates until repaired or deleted.
- Security descriptors are stored when supplied but this layer does not itself enforce access checks.
- `lsa_secret_delete` requires the record to be readable first; a corrupt but present blob may fail deletion through this API.

## Test signals
Tests should create, update, read, and delete a secret in a temporary secrets directory, verifying current/old transitions and timestamp changes. Corrupt-record tests should confirm get/set/delete status mapping. Python binding tests through `passdb.PDB.get_secret`, `set_secret`, and `delete_secret` are useful integration signals.
