# sources/user-network-fs/samba/source3/utils/net_rpc_trust.c

## Purpose
Implements `net rpc trust create` and `net rpc trust delete`, managing LSA trusted-domain objects over RPC. It can operate against one selected domain controller using explicit metadata for the other domain, or against both sides when `otherserver=` is supplied.

## Important APIs, Types, and Functions
Key structures are `enum trust_op`, `struct other_dom_data`, and `struct dom_data`. `parse_trust_args()` parses peer-domain options and optional `trustpw`. `connect_and_get_info()` creates an IPC connection, opens an LSA pipe and policy handle, reads DNS domain policy data, and obtains the LSA session key. `get_trust_domain_passwords_auth_blob()` builds the NDR `trustDomainPasswords` blob. `create_trust()` calls `dcerpc_lsa_CreateTrustedDomainEx2_r()`; `delete_trust()` calls `dcerpc_lsa_DeleteTrustedDomain_r()`.

## Control Flow
`net_rpc_trust()` dispatches to create/delete wrappers and then `rpc_trust_common()`. The command either connects to a peer server or uses supplied peer SID/name values. Create selects AD vs NT4 trust type from the DNS-name argument, uses a supplied or generated trust password, encrypts the auth blob with ARCFOUR using each target LSA session key, and creates trust objects on one or both policy handles. Delete removes the peer SID trust object on one or both sides. Handles, CLI connections, and session keys are cleaned on exit.

## State and Persistence
Persistent state is remote LSA policy: trusted-domain records, trust direction, trust type/attributes, names, SID, and auth information. Local state is transient credentials, session keys, and trust password material.

## Dependencies and Integration Points
Depends on Samba RPC client code, generated LSA/DRS NDR types, SID helpers, GnuTLS cipher helpers, and `net_make_ipc_connection_ex()` from shared net utilities. It is registered under the `net rpc trust` command tree.

## Risks
Wrong peer SID/name arguments can mutate the wrong trust. Two-sided operation can partially succeed if the first side is changed and the second fails. Passing `trustpw=` exposes secrets through command-line surfaces. Crypto/blob handling must remain protocol-compatible.

## Test Signals
Exercise usage failures, explicit-peer and `otherserver` modes, generated and supplied trust passwords, NT4 vs AD trust selection, LSA open failures, cipher failures, partial two-sided failure, and delete by explicit SID.
