
# sources/security-integrity/ima-evm-utils/src/pcr.h

## Purpose
`pcr.h` defines the minimal backend-neutral contract used by `evmctl` to read TPM 2.0 PCR values.

## Important APIs, Types, And Functions
It declares `tpm2_pcr_supported()` and `tpm2_pcr_read(const char *algo_name, uint32_t pcr_handle, uint8_t *hwpcr, int len, char **errmsg)`. Implementations live in IBM TSS, Intel ESAPI, and `tsspcrread` command backends.

## Control Flow
`evmctl` first calls `tpm2_pcr_supported()` before attempting live userspace PCR reads. It then calls `tpm2_pcr_read()` for each supported hash bank and PCR index.

## State And Persistence
The interface is stateless. Implementations may cache paths or allocate error strings, but callers own `errmsg` cleanup when set.

## Dependencies And Integration Points
The contract bridges `evmctl.c` measurement verification and whichever TPM backend was selected at build time.

## Risks
All backends must agree on return codes, digest lengths, algorithm names, and `errmsg` allocation semantics. A mismatch can make measurement verification silently skip banks or produce confusing diagnostics.

## Test Signals
Signals come from `boot_aggregate.test`, `ima_measurement` command coverage, and optional TPM/swtpm setup helpers.
