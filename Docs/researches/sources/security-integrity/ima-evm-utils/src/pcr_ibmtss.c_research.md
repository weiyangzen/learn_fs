
# sources/security-integrity/ima-evm-utils/src/pcr_ibmtss.c

## Purpose
`pcr_ibmtss.c` implements the `pcr.h` interface using IBM TSS library APIs. It reads one TPM 2.0 PCR at a time for the requested hash bank and copies the binary digest into the caller buffer.

## Important APIs, Types, And Functions
`tpm2_pcr_supported()` reports IBM TSS availability. `Algorithm_Map` maps `sha1`, `sha256`, `sha384`, and `sha512` strings to TCG algorithm IDs. `algorithm_string_to_algid()` validates algorithm names. `tpm2_pcr_read()` constructs `PCR_Read_In`, creates a `TSS_CONTEXT`, executes `TPM_CC_PCR_Read`, validates the returned digest count and size, and copies the digest.

## Control Flow
The read path converts the algorithm, creates the TSS context, selects one PCR bit in a three-byte PCR selection, calls `TSS_Execute()`, checks for an allocated bank and matching digest length, then deletes the context regardless of success.

## State And Persistence
No persistent state is stored. `errmsg` may be allocated with `asprintf()` on validation failures. The TPM device state is read-only from this module's perspective.

## Dependencies And Integration Points
It depends on `ibmtss/tss.h`, OpenSSL SHA headers for digest constants, `utils.h`, and libimaevm logging. `evmctl` uses this backend during measurement and boot aggregate commands when compiled with IBM TSS support.

## Risks
Unsupported algorithms return `TPM_ALG_ERROR`. The function validates only returned digest length/count, not the returned selection structure. A non-null `tss_context` is passed to `TSS_Delete()` even after early failures, relying on the library handling null safely. Error text is not produced for every TSS failure path.

## Test Signals
`install-tss.sh` and `install-swtpm.sh` provide CI setup for IBM TSS and software TPM paths. Boot aggregate and measurement list tests are the main behavioral checks.
