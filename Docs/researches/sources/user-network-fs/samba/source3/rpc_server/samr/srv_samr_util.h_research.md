# Research: sources/user-network-fs/samba/source3/rpc_server/samr/srv_samr_util.h

## Purpose

`srv_samr_util.h` declares the SAMR utility surface shared by the SAMR server implementation and adjacent password-change code. It exposes copy helpers for translating generated SAMR user-info levels into passdb `struct samu` records, plus password-change, password-complexity, and AES password-buffer helper declarations implemented in other SAMR source files.

## Important APIs, Types, and Functions

- Forward declaration `struct samu`: keeps the header lightweight while allowing passdb record pointers in prototypes.
- `copy_id*_to_sam_passwd()` and `copy_pwd_expired_to_sam_passwd()`: user-info-to-passdb field copy helpers implemented in `srv_samr_util.c`.
- `chgpasswd()`, `change_oem_password()`, and `pass_oem_change()`: password-change helpers implemented in `srv_samr_chgpasswd.c` and used by SAMR password change/set paths.
- `check_password_complexity_internal()` and `check_password_complexity()`: password policy/complexity hooks used by validation and change paths.
- `samr_set_password_aes()`: decrypts/validates AES-style SAMR encrypted password payloads into plaintext for newer password-change operations.

## Control Flow and Integration

This header does not implement control flow itself. It defines the stable contracts consumed primarily by `srv_samr_nt.c`: set-info operations call copy helpers before passdb persistence, password-change operations call OEM/plaintext/AES helpers, and validation paths call password complexity checks.

## State and Persistence Behavior

The header owns no state. Its declared copy helpers mutate caller-supplied `struct samu` instances; persistence remains a caller responsibility. The password-change declarations imply persistent updates through passdb and optional UNIX password sync in their implementations.

## Dependencies and Integration Points

The declarations use generated SAMR NDR types such as `struct samr_UserInfo21`, `enum samPwdChangeReason`, `struct samr_EncryptedPasswordAES`, and Samba `DATA_BLOB`/`NTSTATUS`/`TALLOC_CTX` types provided by surrounding includes in consumers. It is included by the SAMR RPC server file and the utility implementation.

## Risks and Edge Cases

- Because the header lacks its own include guard in the visible content, it depends on repository build conventions or surrounding generated include patterns to avoid duplicate declarations.
- The API surface mixes simple field-copy helpers with security-sensitive password helpers; callers must understand which functions only stage in-memory changes and which may perform persistent password changes.
- Generated SAMR type changes can break this header and all consumers because the prototypes use concrete generated structs.

## Test Signals

Build tests are the primary signal for this header: generated SAMR type compatibility, duplicate declaration handling, and consumer compile coverage. Functional tests should indirectly cover each declared helper through `_samr_SetUserInfo()`, password-change RPCs, and password validation.
