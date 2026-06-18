# sources/user-network-fs/impacket/examples/raiseChild.py

## Purpose

`raiseChild.py` automates a child-domain to forest privilege escalation workflow based on golden tickets with ExtraSids. Given child-domain administrator credentials, it discovers forest information, obtains child and parent credential material through DRS replication, builds a forged TGT containing the parent Enterprise Admin SID, optionally writes the ticket to a ccache, and optionally launches a PsExec-like shell on a target host.

## Important APIs, Types, and Functions

The file embeds a streamlined RemCom `PSEXEC` implementation plus pipe and shell classes similar to `psexec.py`, adjusted for Kerberos ticket use. `RetryableGoldenTicketError` marks ticket-building failures that should fall through to another credential method.

`RAISECHILD` is the main coordinator. `getChildInfo()` uses NRPC `hDsrGetDcNameEx` to return child domain and forest names. `getParentSidAndTargetName()` uses LSAT/LSAD to read the parent domain SID and resolve a target RID. `__connectDrds()` establishes DRSUAPI with packet privacy, handles DRSBind epoch negotiation, and locates the NTDS DSA object GUID. `DRSCrackNames()` and `DRSGetNCChanges()` locate and replicate target user objects. `__decryptHash()` decrypts `dBCSPwd` and `unicodePwd`; `__decryptSupplementalInfo()` extracts Kerberos AES keys from supplemental credentials.

`makeGolden()` decodes the AS-REP ticket, decrypts `EncTicketPart` with krbtgt key material, extends lifetime, rewrites PAC validation groups, appends the extra SID, signs the PAC, re-encodes authorization data, and re-encrypts the ticket. `raiseUp()` orders AES, RC4, password, and password-derived RC4 attempts for TGT/TGS acquisition and golden ticket validation.

## Control Flow

Main parses the child-domain identity and optional ticket output, target execution host, target RID, and authentication material. `exploit()` discovers the child and forest names, then `raiseUp()` gets the parent Enterprise Admin SID, dumps child `krbtgt`, obtains a child TGT, forges the golden ticket, requests a CIFS TGS for the parent or execution target, uses the forged ticket to DRS-replicate parent `krbtgt` and target user credentials, and returns target credentials plus tickets. `exploit()` writes a ccache when requested and starts the embedded PSEXEC path when `-target-exec` is present.

## State and Persistence Behavior

Remote read operations include NRPC, LSAT, and DRS replication of credential attributes. The forged ticket exists in memory and can be persisted locally with `-w`. If remote execution is requested, the embedded RemCom service flow writes and removes remote service artifacts and opens named pipes. The script prints recovered LM/NT hashes and Kerberos keys to stdout. Internal state caches DRS handles, partial attribute vectors, domain SID, credential dictionaries, and resolved target names.

## Dependencies and Integration Points

It integrates with Impacket Kerberos, PAC, DRSUAPI, NRPC, LSAT/LSAD, SMB, service installation, and RemCom modules, plus `pyasn1` DER encoders/decoders. It depends on DNS/SMB name resolution across child and forest domains, replication privileges in the child domain, compatible KDC encryption types, and trust behavior that accepts ExtraSids.

## Risks and Edge Cases

This is intentionally offensive and high impact: it extracts credential material, forges long-lived tickets, and can execute commands as a privileged parent-domain account. Name resolution failures are common because it converts IPs to DNS names through anonymous SMB. The embedded pipe code contains a likely bug comparing `LastDataSent > 10` where `LastDataSent` is usually bytes/string. `DRSGetNCChanges()` calls `__connectDrds(creds)` with an argument shape inconsistent with `__connectDrds(domainName, creds)`, though normal flows usually connect earlier through `DRSCrackNames()`. The TGS acquired in `raiseUp()` is not passed into final `kerberosLogin()` in `exploit()`, which may require cache/KDC behavior to compensate. Broad exception handling can leave service artifacts behind.

## Test Signals

Test signals include unit-level PAC mutation and signature verification for RC4/AES krbtgt keys, credential attempt ordering and retry behavior, DRS partial attribute set construction, supplemental credential parsing with malformed properties, LSAT target RID resolution, ccache writing from forged TGT, and lab integration in a disposable multi-domain forest for child krbtgt dump, parent target credential dump, and optional service cleanup after `-target-exec`.
