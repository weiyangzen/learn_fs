# sources/user-network-fs/impacket/tests/dcerpc/test_bkrp.py

Purpose: validates the BackupKey Remote Protocol client (`bkrp`) over `\PIPE\protected_storage`, including secret wrapping/restoration and backup public-key retrieval.

Important APIs and functions: `BKRPTests` configures `MSRPC_UUID_BKRP`, SMB named-pipe binding, authenticated packet privacy, and a static `data_in` byte string. Tests exercise raw `bkrp.BackuprKey()` requests and helper `bkrp.hBackuprKey()` for `BACKUPKEY_BACKUP_GUID`, `BACKUPKEY_RESTORE_GUID`, `BACKUPKEY_RESTORE_GUID_WIN2K`, and `BACKUPKEY_RETRIEVE_BACKUP_KEY_GUID`. `bkrp.WRAPPED_SECRET` parses wrapped output, and `cryptography.x509.load_der_x509_certificate()` parses returned certificates.

Control flow: backup tests send plaintext, parse the wrapped response, then submit it to a restore action and assert restored bytes equal `data_in`. Retrieval tests request the backup key with `NULL` input and parse the DER certificate. SMB NDR and NDR64 subclasses run the same suite.

State and persistence behavior: the tests do not write remote state. They depend on domain backup-key service state and may expose backup-key certificate material in printed output.

Dependencies and integration points: depends on `cryptography` for certificate parsing, `tests.dcerpc.DCERPCTests`, and authenticated domain access to Protected Storage/DPAPI backup key RPC.

Risks: missing `cryptography` is only printed at import time, so certificate tests can later fail with `NameError`. These tests require privileges/service availability and packet privacy. They validate sensitive DPAPI backup-key paths and should be run only in controlled labs.

Test signals: strong signal for BKRP NDR marshalling, helper wrappers, backup/restore round trips, NDR64 compatibility, and certificate blob parsing.
