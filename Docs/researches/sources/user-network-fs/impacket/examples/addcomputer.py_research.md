# sources/user-network-fs/impacket/examples/addcomputer.py

## Purpose

`addcomputer.py` adds, deletes, or changes the password of an Active Directory computer account using either SAMR over SMB or LDAPS. It implements the common machine-account quota path and supports Kerberos, NTLM hashes, AES keys, explicit DC host/IP, and custom OU placement for LDAPS.

## Important APIs, Types, and Functions

`ADDCOMPUTER.__init__` validates options, derives target/DC settings, normalizes computer names with trailing `$`, generates random passwords, derives base DN and computer container for LDAPS, and selects default ports. `run_samr` creates a SAMR DCERPC transport. `run_ldaps` uses `init_ldap_session` and LDAP add/modify/delete operations. `LDAPComputerExists`, `LDAPGetComputer`, and `generateComputerName` support LDAP mode. `doSAMRAdd` performs domain lookup, account existence checks, user creation/open/delete, password set, and workstation trust account control updates through SAMR calls.

## Control Flow

CLI parsing produces account credentials and action/method options. `run` dispatches to SAMR or LDAPS. SAMR mode connects to `\pipe\samr`, enumerates domains excluding Builtin, selects a domain, opens it with lookup/create rights, verifies target account existence for delete/password-reset or non-existence for add, creates or opens the user handle, deletes or sets the internal password, and for new accounts reopens the user to set workstation-trust UAC. LDAPS mode binds over LDAP SSL, validates existing or absent computer objects, then deletes, modifies `unicodePwd`, or adds a computer object with DNS hostname, SPNs, UAC, `sAMAccountName`, and password.

## State and Persistence Behavior

This script mutates Active Directory. It can create computer accounts, set/reset computer passwords, delete accounts, set SPNs/DNS hostnames, and assign UAC values. It logs generated computer passwords in cleartext. SAMR handles and LDAP connections are closed in finally paths where possible.

## Dependencies and Integration Points

It depends on Impacket SAMR/EPM/DCERPC transport, SPNEGO imports, Impacket LDAP session helpers, `ldap3`, Kerberos/NTLM credential handling, and AD domain policies such as machine account quota and LDAPS password-change requirements.

## Risks and Edge Cases

This is high-impact code because it changes AD objects. Generated passwords and provided passwords appear in logs. LDAPS object creation uses a caller-provided `computer_group` DN without escaping. SAMR domain selection can fail on multi-domain servers unless `-domain-netbios` is accurate. The import `ldap3_kerberos_login` is unused. Error handling logs critical messages but often swallows exceptions inside mode methods, so callers may not get a nonzero failure signal. Kerberos requires `-dc-host`, and target IP/name handling must be exact.

## Test Signals

Unit tests can mock SAMR and LDAP calls to verify option validation, generated names/passwords, SPN construction, base DN derivation, and error mapping for access denied/quota exceeded/not found. Integration tests require an AD lab and should verify add, no-add password reset, delete, SAMR versus LDAPS, Kerberos and NTLM, multi-domain selection, and cleanup of created accounts.
