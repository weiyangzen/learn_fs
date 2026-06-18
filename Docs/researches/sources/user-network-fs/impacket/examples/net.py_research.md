# sources/user-network-fs/impacket/examples/net.py

## Purpose

`net.py` is an Impacket alternative to Windows `net.exe` for remote account and group administration over SMB-backed DCE/RPC. It exposes `user`, `computer`, `group`, and `localgroup` subcommands that enumerate, query, create, delete, enable/disable, and modify membership for SAM objects on a remote host or domain controller.

## Important APIs, Types, and Functions

The core abstractions are `LsaTranslator`, `SamrObject`, `User`, `Computer`, `Group`, `Localgroup`, and `Net`. `LsaTranslator` binds to `\pipe\lsarpc` and wraps `hLsarLookupNames3` and `hLsarLookupSids2` for SID/name conversion. `SamrObject` binds to `\pipe\samr`, opens builtin or account domains, resolves RIDs, and opens SAMR user, group, or alias handles.

`User` implements `Enumerate`, `Query`, `Create`, `Remove`, and `SetUserAccountControl`; `Computer` reuses `User` with workstation/server trust account flags. `Group` calls `hSamrEnumerateGroupsInDomain`, `hSamrGetMembersInGroup`, `hSamrAddMemberToGroup`, and `hSamrRemoveMemberFromGroup`. `Localgroup` switches to builtin aliases and uses SID-based `hSamrGetMembersInAlias`, `hSamrAddMemberToAlias`, and `hSamrRemoveMemberFromAlias`.

The `Net` facade parses credentials and action options, creates an `SMBConnection`, logs in with NTLM or Kerberos, dispatches to an action class by capitalizing the subcommand name, and formats account details.

## Control Flow

Command-line parsing builds a required subparser for the target object type and validates that `-name` accompanies join/unjoin and `-newPasswd` accompanies create. `parse_target` extracts domain, username, password, and address; missing passwords are prompted unless hashes, AES, Kerberos cache, or no-pass mode are selected. `Net.run()` connects, instantiates the selected action object, then executes exactly one operation by option precedence: create, remove, enable, disable, join, unjoin, query by name, or enumerate.

Querying a user is the richest path: it opens the account domain, retrieves `UserAllInformation`, collects global group RIDs, converts them to names, then reopens the builtin domain to resolve local alias memberships from constructed SID arrays.

## State and Persistence Behavior

The script mutates remote SAM state for create/delete, account-control, and membership operations. It stores only transient handles and connection state locally. SAMR domain handles are cached inside `SamrObject` but closed after operations. No local files are written. Passwords and hashes exist in process memory, and created users/computers are enabled after password setup.

## Dependencies and Integration Points

Integration points are `impacket.smbconnection.SMBConnection`, DCE/RPC transport factories, SAMR (`impacket.dcerpc.v5.samr`), LSAD/LSAT, `parse_target`, and the shared Impacket example logger. The script depends on remote named pipes `samr` and `lsarpc`, SMB port 139 or 445, and the caller having sufficient account-management privileges.

## Risks and Edge Cases

`__get_action_class()` resolves classes dynamically from the subcommand name, so parser choices are the main guard against unexpected dispatch. `User._hEnableAccount()` toggles the disabled bit with XOR; if called for an already-enabled account, it would set the disabled bit, although the public flow labels it as enable. Domain selection uses a fixed enumerated-domain index for builtin versus account domains, which can be brittle if server ordering differs. Several `STATUS_MORE_ENTRIES` paths ignore pagination beyond the first response. Group/localgroup option help strings are swapped, and success messages contain typos but not behavioral issues.

## Test Signals

Useful tests include parser validation for missing `-name` and `-newPasswd`, mocked SAMR/LSAT calls for class dispatch and handle closure, enumeration when SAMR raises `STATUS_MORE_ENTRIES`, user query formatting for never-expiring FILETIME values, and integration tests against a disposable AD lab for create/remove, enable/disable, and domain versus builtin membership changes.
