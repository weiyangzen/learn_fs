
# sources/security-integrity/ima-evm-utils/src/evmctl.c

## Purpose
`evmctl.c` implements the `evmctl` command-line utility for Linux IMA/EVM workflows. It signs and verifies EVM metadata signatures, IMA file signatures and hashes, imports public keys into kernel keyrings, writes IMA xattrs from signature files, recursively fixes or clears IMA/EVM xattrs, signs precomputed hashes including fs-verity digests, verifies IMA measurement lists against TPM PCRs, and calculates boot aggregate digests.

## Important APIs, Types, And Functions
The CLI is organized around `struct command cmds[]`, `struct option opts[]`, and `main()` option parsing. Global state captures selected hash/key/signature behavior: `g_hash_algo`, `imaevm_params.keyfile`, `g_keypass`, `sigflags`, `g_signature_version`, xattr namespace names, EVM metadata overrides, PCR file options, and OpenSSL engine/provider access.

Core file/xattr functions include `hash_ima()`, `sign_ima()`, `sign_evm()`, `verify_ima()`, `verify_evm()`, `setxattr_ima()`, `calc_evm_hash()`, and `calc_evm_hmac()`. Recursive traversal is handled by `do_cmd()`, `get_file_type()`, `find()`, `ima_fix()`, and `ima_clear()`. Measurement handling is centered on `struct template_entry`, `ima_measurement()`, `ima_ng_show()`, `extend_tpm_banks()`, `compare_tpm_banks()`, and `cmd_ima_bootaggr()`.

## Control Flow
`main()` initializes OpenSSL, parses global options, configures optional PKCS#11 engine/provider access, then dispatches by command name through `call_command()`. Signing commands calculate a digest from file data or EVM metadata, call libimaevm signing routines, prepend the xattr type where needed, and either print/write `.sig` files or set `security.ima`/`security.evm` xattrs. Verification commands load one or more X.509 public keys, recover the signature hash algorithm, recompute the relevant digest, and call libimaevm verification.

IMA measurement replay reads a binary measurement list record by record, reconstructs per-bank PCR extends, optionally verifies template hashes and template signatures, and compares recalculated banks to TPM/sysfs/user-supplied PCR values after each entry. Boot aggregate calculation reads either live PCRs or a TPM 1.2 BIOS event log, hashes PCRs 0-7 for SHA1 or 0-9 for other banks, and prints `<algo>:<digest>` lines.

## State And Persistence
Persistent effects are direct and security-sensitive: xattrs are written or removed, `.sig` sidecar files may be created, kernel keyrings may receive public keys, and request results depend on live TPM/sysfs state. `find()` changes process working directory during recursion and restores via `chdir("..")`, so relative paths and errors during recursion are important. Global option state is process-local but widely shared across handlers.

## Dependencies And Integration Points
The file integrates libimaevm, OpenSSL EVP/HMAC/RSA/X.509, Linux xattrs, keyutils, filesystem `FS_IOC_GETVERSION`, TPM PCR helpers via `pcr.h`, `blkid` through `popen()`, and Linux IMA/EVM xattr conventions. Compile-time gates control deprecated signature-v1, OpenSSL engine/provider, and debug-only HMAC command support.

## Risks
The EVM digest format is sensitive to metadata width, inode/generation/UUID portability flags, xattr ordering, and optional override strings. Several parsers use fixed-size buffers and assertions; malformed signature/hash input or unexpected xattr sizes can fail hard. `find()` ignores callback return values for child recursion in some paths and relies on `dirent.d_type`, which can be `DT_UNKNOWN` on some filesystems. The measurement parser exits on some malformed records, mixes endianness assumptions with binary log data, and supports only known template layouts. PKCS#11 usage requires key IDs and provider/engine setup, otherwise signing fails late.

## Test Signals
Relevant tests are declared in `tests/Makefile.am` and `tests/kernel/Makefile.am`: `ima_hash.test`, `sign_verify.test`, `boot_aggregate.test`, `ima_policy_check.test`, plus kernel tests for fs-verity, portable signatures, mmap checks, EVM HMAC, non-action rule flags, and creds checks. `functions.sh`, `gen-keys.sh`, `softhsm_setup`, and install helper scripts provide key material, PKCS#11, TPM, OpenSSL, and fs-verity prerequisites.
