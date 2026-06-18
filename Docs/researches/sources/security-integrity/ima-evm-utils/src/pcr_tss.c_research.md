
# sources/security-integrity/ima-evm-utils/src/pcr_tss.c

## Purpose
`pcr_tss.c` implements the `pcr.h` interface using Intel TSS2 ESAPI. It reads a selected TPM 2.0 PCR and verifies that the TPM returned exactly the requested selection and digest size.

## Important APIs, Types, And Functions
`tpm2_pcr_supported()` logs the selected TSS2 library. `algo_to_tss2()` maps string names to `TPM2_ALG_*`. `pcr_selections_match()` compares TPM selection structures. `tpm2_set_errmsg()` formats TSS2 errors, optionally using `Tss2_RC_Decode()`. `tpm2_pcr_read()` initializes ESAPI, calls `Esys_PCR_Read()`, validates selection and digest count/size, copies the digest, and frees ESAPI allocations.

## Control Flow
The function builds a single-bank, single-PCR selection, initializes `ESYS_CONTEXT`, performs an unauthenticated PCR read, finalizes the context, validates the output selection, then returns the digest or an allocated error string.

## State And Persistence
The module holds no persistent state. It allocates and frees ESAPI-returned structures for each read.

## Dependencies And Integration Points
It depends on `tss2/tss2_esys.h` and optionally `tss2/tss2_rc.h`. It is an interchangeable PCR backend for `evmctl` measurement verification.

## Risks
The ABI version is hard-coded, which can matter with older or newer TSS2 stacks. Error formatting writes through `errmsg`; callers must free allocated text. The backend returns failure for any selection mismatch, which is appropriate but can expose TPM/library quirks.

## Test Signals
Measurement and boot aggregate commands exercise it when built with ESAPI. A TPM simulator or hardware TPM is required for live end-to-end validation.
