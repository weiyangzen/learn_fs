# sources/user-network-fs/impacket/examples/dpapidump.py

## Purpose
`dpapidump.py` remotely extracts and decrypts DPAPI-protected SYSTEM credentials and SCCM client secrets from a Windows host. It combines SMB file collection, optional WMI queries for SCCM policy secrets, and LSA secret extraction to obtain the SYSTEM DPAPI user key.

## Important APIs, Types, and Functions
`DumpCreds` owns the workflow. `connect()` creates an SMB session with NTLM or Kerberos. `getDPAPI_SYSTEM()` captures the SYSTEM DPAPI user key from LSA secret callbacks. `getFileContent()` reads remote files into memory. `decideBlobMasterkey()` tracks required masterkey GUIDs. `addPolicySecret()` enumerates WMI records, extracts XML CDATA policy secret blobs with regex, wraps them as `DPAPI_BLOB`, and records required masterkeys. `dump()` performs SCCM enumeration, credential/masterkey retrieval, LSA extraction, masterkey decryption, and final secret decryption. `cleanup()` tears down remote registry operations.

The script uses `DCOMConnection` and WMI interfaces, `SMBConnection`, `RemoteOperations` and `LSASecrets` from `examples.regsecrets`, Impacket DPAPI structures, Kerberos keytab loading, and configurable RPC auth levels.

## Control Flow
Main parses target and options, resolves credentials, handles target IP, prompts for passwords, processes AES/keytab/hashes, parses COM version, and sets `options.all` when neither `-sccm` nor `-creds` is selected. `DumpCreds.dump()` first queries SCCM WMI namespaces and policy classes when requested. It then connects over SMB, lists SYSTEM profile credential directories, reads credential blobs, derives masterkey IDs, fetches corresponding masterkey files under `C$\Windows\System32\Microsoft\Protect\S-1-5-18\User\`, and fetches masterkeys required by SCCM blobs. If no `-userkey` is provided, it enables remote registry, obtains the bootkey, and dumps LSA secrets for the DPAPI user key. Finally it decrypts masterkeys and uses them to decrypt SCCM secrets and credential files.

## State and Persistence
The tool keeps collected raw credentials, raw masterkeys, decrypted masterkeys, SCCM secrets, and required masterkey IDs in dictionaries/lists. It does not intentionally write output files, but it enables remote registry services through `RemoteOperations` and later calls `finish()` for cleanup. It prints decrypted secrets to logs/stdout.

## Dependencies and Integration Points
Integration points are remote SMB admin shares, WMI/DCOM SCCM namespaces, remote registry/LSA secret extraction, Kerberos credential cache/keytab, and DPAPI blob parsing. It can use RPC packet privacy or integrity for WMI services.

## Risks
The script extracts highly sensitive SYSTEM credentials and SCCM Network Access Account secrets. Missing cleanup can leave remote registry service state changed if the process is interrupted outside handled paths. WMI regex parsing assumes a specific `PolicySecret` XML shape and can fail on malformed records. Broad exception handlers can continue with partial data, making output completeness hard to judge. It logs decrypted user keys and secrets.

## Test Signals
Tests should cover SCCM XML blob parsing, masterkey ID tracking, credential-to-masterkey lookup, userkey-supplied mode versus LSA-dump mode, no-credentials/no-SCCM paths, Kerberos fallback behavior, RPC auth level setting, and cleanup on exceptions. Integration tests need Windows hosts with and without SCCM policy, SYSTEM credential files, denied admin shares, and provided bootkey/userkey scenarios.
