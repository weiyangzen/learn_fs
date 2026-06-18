# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/ldapattack.py

## Purpose
`ldapattack.py` is the main LDAP/LDAPS relay attack implementation for ntlmrelayx. It can launch an interactive LDAP shell, validate relayed-user privileges, perform ACL-based DCSync escalation, add users/computers, add users to privileged groups, configure resource-based constrained delegation, add shadow credentials, dump domain/LAPS/gMSA/ADCS data, and create AD-integrated DNS records.

## Important APIs, Types, and Functions
- Global flags `dumpedDomain`, `dumpedAdcs`, `alreadyEscalated`, `alreadyAddedComputer`, and `delegatePerformed` prevent repeat actions in one process.
- `MSDS_MANAGEDPASSWORD_BLOB(Structure)` parses gMSA managed password blobs and slices current/previous password intervals.
- `LDAPAttack(ProtocolAttack)` registers `PLUGIN_NAMES = ["LDAP", "LDAPS"]`.
- Core mutators include `addComputer()`, `addUser()`, `addUserToGroup()`, `shadowCredentialsAttack()`, `delegateAttack()`, `aclAttack()`, `writeRestoreData()`, and `addDnsRecord()`.
- Discovery helpers include `validatePrivileges()`, `getUserInfo()`, `checkSecurityDescriptors()`, `aceApplies()`, and `dumpADCS()`.
- Module helpers `create_object_ace()`, `create_allow_ace()`, `create_empty_sd()`, `can_create_users()`, and `can_add_member()` build and inspect LDAP ACL structures.

## Control Flow
`run()` creates a `ldapdomaindump.domainDumper`, launches `LdapShell` in interactive mode if configured, optionally validates privileges by enumerating the relayed account's SID, recursive group SIDs, primary group, domain/OUs/Users container security descriptors, and interesting privileged groups. It then conditionally performs ACL attack, group escalation, LAPS dump, gMSA dump, ADCS dump, DNS record addition, computer addition, RBCD delegation for machine accounts, shadow credentials, and finally domain dump.

`aclAttack()` reads the domain DACL, appends replication rights ACEs for the chosen user SID, writes the descriptor back, re-reads the result, and stores restore JSON. `delegateAttack()` adds an ACE to `msDS-AllowedToActOnBehalfOfOtherIdentity`. `shadowCredentialsAttack()` appends a `KeyCredential` DN-binary value and exports PEM or PFX material. `addDnsRecord()` builds raw DNS node records and creates `dnsNode` objects, with a special WPAD bypass path.

## State and Persistence Behavior
Remote AD state may be changed extensively: new users/computers, group membership, domain DACL replication rights, RBCD descriptors, shadow credentials, DNS nodes, and LDAP StartTLS state. Local outputs include domain dump files under `config.lootdir`, LAPS/gMSA dump files in the working directory, ACL restore JSON, and shadow credential PEM/PFX files. Module-level globals make behavior process-wide rather than per target.

## Dependencies and Integration Points
The module depends on `ldap3`, `ldapdomaindump`, `dns.resolver`, `Cryptodome.Hash.MD4`, Impacket LDAP/security descriptor types, `impacket.uuid`, `impacket.structure`, `LdapShell`, `TcpShell`, and `shadow_credentials`. It is loaded by the ntlmrelayx attack registry and consumes many ntlmrelayx config flags.

## Risks and Edge Cases
- Global one-shot flags are not keyed by domain/target and can suppress legitimate operations across different relays.
- Many operations are high-impact and require cleanup; DNS creation logs cleanup instructions but does not automate cleanup.
- Generated credentials and certificate material are logged or written to local disk.
- Security descriptor writes can overwrite concurrent changes and may fail under constrained delegation/channel binding policies.
- Broad `except` blocks in dump paths can hide parse or permission errors.
- Privilege validation can be expensive in large domains.
- `addDnsRecord()` directly constructs binary DNS records and assumes SOA lookup and naming contexts are available.

## Test Signals
Unit tests should mock LDAP responses for privilege validation, ACE applicability, DACL mutation, restore-data writing, gMSA blob parsing/NT hash derivation, ADCS enrollment parsing, DNS record byte construction, and StartTLS fallback. Lab integration tests should cover ACL escalation, RBCD, shadow credentials, LAPS/gMSA reads, add-computer/add-user, and DNS record creation/cleanup.
