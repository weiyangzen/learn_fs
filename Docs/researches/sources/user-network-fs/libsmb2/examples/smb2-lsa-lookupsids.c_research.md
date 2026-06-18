# sources/user-network-fs/libsmb2/examples/smb2-lsa-lookupsids.c

Purpose: This example connects to the LSA DCE/RPC service over SMB IPC and performs a `LookupSids2` request for built-in administrator SID data.

Important APIs and types: It uses `dcerpc_context`, `lsa_interface`, `lsa_OpenPolicy2`, `lsa_LookupSids2`, `lsa_Close`, `RPC_SID`, `ndr_context_handle`, `POLICY_LOOKUP_NAMES`, `POLICY_VIEW_LOCAL_INFORMATION`, and libsmb2 IPC connection APIs.

Control flow: The program connects to `IPC$`, creates a DCE/RPC context, asynchronously binds to `lsarpc`, opens a policy handle for `\\server`, builds SID `S-1-5-32-544`, calls `LookupSids2`, prints referenced domains and translated names, closes the policy handle, and drives all async DCE/RPC calls via the SMB2 poll loop.

State and persistence behavior: Runtime state includes global `is_finished`, `PolicyHandle`, allocated SID arrays, and DCE/RPC decoded replies. There is no persistence.

Dependencies and integration points: It validates the DCE/RPC layer, LSA generated coders, IPC$ tree connect, authentication/user propagation, and SMB2 event servicing.

Risks: The same SID pointer is inserted twice into the request array, which is acceptable for this probe but not a general pattern. Error paths exit without full cleanup. It assumes the target server supports LSA over named pipes and permits the lookup.

Test signals: Successful output lists referenced domains and translated names for the built-in administrators SID. Failures distinguish IPC connect, DCE bind, policy open, lookup, and close stages.
