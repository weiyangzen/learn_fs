<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_generate_tpm_key.c -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_generate_tpm_key.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_generate_tpm_key.c_research.md`. Source lines read for this pass: 262.

## Purpose
Optional TSPI utility that creates a TPM storage key bound to selected current PCR values and registers it in persistent storage.

## Important APIs, Types, And Functions
Functions `usage`, `util_bytes_to_string`, and `main`; TSPI calls include context creation/connection, TPM object lookup, PCR reads, PCR composite setup, SRK load, policy secret setup, RSA key creation, random UUID generation, and key registration.

## Control Flow
Parses repeated `-p PCR` options, queries the TPM PCR count, validates selected PCRs, reads their current values into a PCR composite, loads the SRK with the well-known secret, creates a 2048-bit volatile non-migratable storage key, registers it under a random UUID, and prints selected PCR values and UUID.

## State And Persistence Behavior
Writes a key into TSPI user persistent storage and allocates/frees TPM context memory.

## Dependencies And Integration Points
Built only with `BUILD_TSPI`; depends on TrouSerS/TSPI headers and libraries and an accessible TPM.

## Risks And Edge Cases
Legacy TPM 1.2 assumptions, well-known SRK secret, PCR off-by-one validation (`>` rather than `>=`) risk, and sparse memory cleanup on error paths.

## Test Signals
Requires TPM/TSPI integration hardware or emulator; verify PCR-bound key registration and reported UUID can be used by the key module.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs_generate_tpm_key.c -->
