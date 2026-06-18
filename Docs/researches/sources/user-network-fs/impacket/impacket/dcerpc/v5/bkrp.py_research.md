# sources/user-network-fs/impacket/impacket/dcerpc/v5/bkrp.py

## Purpose

`bkrp.py` implements the BackupKey Remote Protocol interface. It defines the BKRP UUID, action-agent GUID constants, wire structures for wrapped secrets, the `BackuprKey` RPC call, opnum mapping, and a helper for invoking the service.

## Important APIs, Types, and Functions

`MSRPC_UUID_BKRP` identifies the interface. Action constants include `BACKUPKEY_BACKUP_GUID`, `BACKUPKEY_RESTORE_GUID_WIN2K`, `BACKUPKEY_RETRIEVE_BACKUP_KEY_GUID`, and `BACKUPKEY_RESTORE_GUID`. `BYTE_ARRAY` and `PBYTE_ARRAY` model conformant byte arrays. `Rc4EncryptedPayload` and `WRAPPED_SECRET` parse MS-BKRP wrapped secret payloads. `BackuprKey` and `BackuprKeyResponse` define opnum 0, with `OPNUMS` mapping that pair. `hBackuprKey` fills input data length and sends the request.

## Control Flow

Callers bind to `MSRPC_UUID_BKRP` and invoke `hBackuprKey` with an action GUID and input bytes. The helper sets `cbDataIn` to zero for `NULL` input or to `len(pDataIn)` otherwise, assigns `dwParam`, and calls `dce.request`. The server response returns an output byte array pointer, output length, and NTSTATUS `ErrorCode`.

## State and Persistence Behavior

The module is stateless locally. The remote service may unwrap, wrap, or return backup keys depending on the action GUID and caller authorization. Parsed `WRAPPED_SECRET` instances are in-memory views over binary payloads.

## Dependencies and Integration Points

It depends on Impacket NDR classes, DCE/RPC types, `system_errors`, UUID conversion, `Structure`, and `DCERPCException`. It integrates with DPAPI and domain backup key workflows that need to call domain controllers' BackupKey service.

## Risks and Edge Cases

The file has a TODO for client-side-wrapped secret support. `WRAPPED_SECRET` only models the RC4 encrypted payload form visible here and does not implement cryptographic verification or decryption. `hBackuprKey` trusts `pDataIn` length and type. BKRP operations are highly sensitive because they can expose or use domain DPAPI backup keys, so tests and tools must avoid accidental production key retrieval.

## Test Signals

Tests should verify UUID/action GUID encodings, NDR serialization for `BackuprKey`, `NULL` input length behavior, `WRAPPED_SECRET` parsing on fixture blobs, and NTSTATUS error formatting. Integration tests require a controlled domain controller or a mocked DCE/RPC server.
