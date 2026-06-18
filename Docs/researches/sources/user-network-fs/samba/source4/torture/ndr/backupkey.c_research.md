# sources/user-network-fs/samba/source4/torture/ndr/backupkey.c

## Purpose
`backupkey.c` adds a focused Samba torture NDR test for the BackupKey RPC data type `bkrp_exported_RSA_key_pair`. It embeds one captured NDR byte stream, `exported_rsa_ndr`, representing an exported RSA key pair and certificate-like payload, then verifies that Samba's generated BackupKey NDR pull and push routines can parse and re-emit the structure without changing the encoded bytes.

## Important APIs, types, and functions
- `exported_rsa_ndr` is the static binary fixture. The data starts with BackupKey/RSA metadata and includes a large RSA public/private key and X.509-style certificate material.
- `ndr_backupkey_suite(TALLOC_CTX *ctx)` is the exported suite factory consumed by the parent NDR torture suite.
- `torture_suite_create(ctx, "backupkey")` creates the child suite.
- `torture_suite_add_ndr_pull_validate_test(..., bkrp_exported_RSA_key_pair, exported_rsa_ndr, NULL)` registers a pull-and-push validation test using generated functions from `librpc/gen_ndr/ndr_backupkey.h`.

## Control flow
At test-suite construction time, the file creates a `backupkey` suite and registers one generated NDR validation case. The torture helper pulls `exported_rsa_ndr` into `struct bkrp_exported_RSA_key_pair`, optionally prints it through the generated printer, pushes it back through `ndr_push_bkrp_exported_RSA_key_pair`, and compares the result against the original fixture. No custom check callback is supplied, so the behavioral assertion is round-trip fidelity rather than semantic field-by-field validation.

## State and persistence behavior
The file has no mutable process state and no external persistence. The only state is the compile-time `static const` byte array and the transient talloc-backed objects allocated by the shared NDR torture harness when the suite runs.

## Dependencies and integration points
The file depends on Samba's common includes, `torture/ndr/ndr.h` for NDR torture registration macros, generated BackupKey NDR declarations from `ndr_backupkey.h`, and `torture/ndr/proto.h` for suite prototypes. It is integrated into the overall NDR suite by `source4/torture/ndr/ndr.c`, which adds `ndr_backupkey_suite(suite)` under the larger `ndr` test family.

## Risks and edge cases
- Because the custom check callback is `NULL`, regressions that decode to semantically wrong in-memory fields but happen to push back to identical bytes may not be caught.
- The fixture is large cryptographic material; accidental byte edits are hard to review manually and would change test meaning.
- The test covers one exported RSA key pair shape only. It does not exercise malformed BackupKey data, alternate key sizes, or failure paths.
- Round-trip validation is sensitive to intentional encoder canonicalization changes; generated NDR push behavior must preserve this fixture exactly.

## Test signals
The test signal is a successful `backupkey` NDR torture subtest. It proves generated pull/push support for `bkrp_exported_RSA_key_pair` can consume this captured Windows-style BackupKey RSA export and reproduce the same NDR stream.
