# sources/user-network-fs/samba/source3/passdb/pdb_secrets.h

## Purpose
`pdb_secrets.h` is the public passdb header for the secrets helper implemented in `pdb_secrets.c`. It exposes trusted-domain enumeration from the secrets database to other passdb code.

## Important APIs, Types, And Functions
The header declares `secrets_trusted_domains(TALLOC_CTX *mem_ctx, uint32_t *num_domains, struct trustdom_info ***domains)`. The caller supplies a talloc context and receives a count plus an array of `struct trustdom_info *` entries.

## Control Flow
There is no executable control flow. Include guards prevent duplicate inclusion. The declaration maps directly to the implementation that initializes secrets and traverses `secrets.tdb`.

## State And Persistence
The header has no state. It documents an API that reads persistent trust records from `secrets.tdb`.

## Dependencies And Integration Points
This header is included by passdb modules that need source3 secrets-backed trusted-domain data. It is intentionally narrow and does not expose the `PDB_secrets_*` wrapper declarations present in the C file, so those wrappers are likely declared through another generated or central passdb header path.

## Risks
Because the header declares only `secrets_trusted_domains()`, consumers relying on the uppercase wrapper helpers need declarations elsewhere; missing prototypes would be a build-time signal. The API returns an allocated array of pointers, so callers must use the supplied talloc context correctly.

## Test Signals
Build coverage is the main signal: consumers should compile with this header and resolve `secrets_trusted_domains()`. Runtime tests belong with `pdb_secrets.c` and should verify the returned array lifetime under the caller's talloc context.
