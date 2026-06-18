# sources/user-network-fs/impacket/examples/dpapi.py

## Purpose
`dpapi.py` is a local and remote DPAPI/Vault inspection utility. It can parse and decrypt masterkey files, retrieve domain backup keys, decrypt credential files, decrypt vault policy/credential files, unprotect raw DPAPI blobs, and parse/decrypt CREDHIST entries.

## Important APIs, Types, and Functions
`DPAPI` is the main executor. `getDPAPI_SYSTEM()` extracts machine and user DPAPI keys from LSA secret callbacks, and `getLSA()` uses `LocalOperations` and `LSASecrets` to read local hive material. `run()` dispatches on subcommands: `MASTERKEY`, `BACKUPKEYS`, `CREDENTIAL`, `VAULT`, `UNPROTECT`, and `CREDHIST`.

The script uses many Impacket DPAPI structures: `MasterKeyFile`, `MasterKey`, `CredHist`, `DomainKey`, `CredentialFile`, `DPAPI_BLOB`, `CREDENTIAL_BLOB`, `VAULT_VCRD`, `VAULT_VPOL`, `VAULT_VPOL_KEYS`, `P_BACKUP_KEY`, `PREFERRED_BACKUP_KEY`, `PVK_FILE_HDR`, `PRIVATE_KEY_BLOB`, `DPAPI_DOMAIN_RSA_MASTER_KEY`, `deriveKeysFromUser()`, `deriveKeysFromUserkey()`, and `CREDHIST_FILE`. Remote domain backup operations use SMB, LSAD over `\pipe\lsarpc`, and BKRP over `\PIPE\protected_storage`.

## Control Flow
`argparse` defines subcommands and shared logging. `MASTERKEY` parses the masterkey file, slices optional backup, credhist, and domain key sections, then tries decryption with local hives, SID plus system keys, provided raw key, PVK domain backup key, password-derived user keys, or remote BKRP restore. `BACKUPKEYS` authenticates to a DC, retrieves LSA private data for backup keys, and prints or exports legacy/preferred key material. `CREDENTIAL`, `VAULT`, `UNPROTECT`, and `CREDHIST` parse their respective files and decrypt only when the required key/password/entropy is supplied.

## State and Persistence
Most modes read files and print parsed or decrypted material. `BACKUPKEYS --export` writes `.key`, `.der`, and `.pvk` files named after domain backup key secrets. Remote masterkey decryption creates network sessions but no intentional local state. Sensitive decrypted keys and secrets are printed to stdout.

## Dependencies and Integration Points
The script integrates with offline Windows hive parsing, LSA secrets, SMB, LSARPC, BKRP, RSA/PVK conversion, AES vault decryption, and Impacket DPAPI structures. It bridges local forensic workflows and domain-controller-assisted DPAPI recovery.

## Risks
This utility exposes high-value DPAPI masterkeys, backup keys, vault contents, credentials, and password history. Several file reads and writes do not use context managers, and broad exception handling can obscure partial failures. It references `options` rather than `self.options` in multiple branches, relying on the global name from `__main__`. Exported backup keys are unprotected files in the current directory.

## Test Signals
Tests should cover each subcommand with known DPAPI fixtures: masterkeys decryptable by password, raw key, hive-derived keys, and PVK; vault VCRD/VPOL decrypt; credential blob decrypt; CREDHIST full and indexed decrypt; and backup key export formatting. Integration tests need a domain lab for LSARPC/BKRP and local hive fixtures for `getLSA()`.
