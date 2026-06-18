# sources/user-network-fs/impacket/tests/dcerpc/test_lsad.py

Purpose: broad integration coverage for Local Security Authority Policy (`lsad`) RPC over `\PIPE\lsarpc`, including policy queries, account/privilege management, secret/private-data APIs, security descriptors, forest trust queries, and policy mutation.

Important APIs and functions: `LSADTests.open_policy()` obtains a policy handle with `MAXIMUM_ALLOWED`, `POLICY_CREATE_SECRET`, `DELETE`, and `POLICY_VIEW_LOCAL_INFORMATION`. Tests cover raw/helper `LsarOpenPolicy`, `LsarOpenPolicy2`, `LsarQueryInformationPolicy(2)`, `LsarQueryDomainInformationPolicy`, account enumeration/open/create/delete, privilege add/remove/enumerate/lookup/display, account rights add/remove, secret create/open/set/query/delete, private data retrieve/store, security query/set, forest trust query, and `LsarSetInformationPolicy(2)`.

Control flow: most tests connect, open a policy handle, build an NDR request or helper call, dump responses, and sometimes assert round-trip values. Account mutation tests derive the account domain SID and append RID `9999` for temporary account operations. Secret tests create `MYSECRET`, open it, attempt to set encrypted values, then delete it. Private-data tests copy `DPAPI_SYSTEM` encrypted data into key `BETUS` and then remove it by storing `NULL`. Audit-policy tests read `AuditingMode`, set it to zero, re-read, and restore the old value.

State and persistence behavior: many tests mutate remote LSA state but usually clean up: temporary accounts are deleted, privileges/right changes are removed, secrets are deleted, private data `BETUS` is cleared, and audit policy is restored. If an exception interrupts cleanup outside guarded blocks, residue or policy changes can remain.

Dependencies and integration points: depends on authenticated LSA RPC, administrative or high-privilege rights for many operations, `impacket.dcerpc.v5.lsad` structures, NDR/NDR64 transfer syntax, and Windows/domain policy semantics.

Risks: high operational risk in non-disposable environments. Some operations touch sensitive secrets (`DPAPI_SYSTEM`) and security policy. Cleanup is inconsistent: several tests do not use `finally`. Broad `MAXIMUM_ALLOWED` requests and policy changes can fail due to UAC/LSA protection/domain policy. Some exception handling accepts expected domain-specific status strings.

Test signals: provides extensive marshalling and helper parity coverage for LSAD unions, handles, SIDs, LUID privileges, unicode strings, security descriptors, encrypted secret blobs, mutable policy information, and NDR64 compatibility.
