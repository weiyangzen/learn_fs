# sources/user-network-fs/impacket/examples/checkMSSQLStatus.py

## Purpose
`checkMSSQLStatus.py` checks whether a Microsoft SQL Server enforces Channel Binding Token validation during Windows authentication. It does this by performing two logins: one with the real CBT computed by Impacket's TDS layer and one with an intentionally invalid empty CBT.

## Important APIs, Types, and Functions
`MSQLCBTCheck` carries parsed CLI options and connection identity. `_new_conn()` creates and connects an `impacket.tds.MSSQL` client. `_login()` chooses between `MSSQL.kerberosLogin()` and `MSSQL.login()` and passes `cbt_fake_value` as either `None` or `b''`. `run()` drives pre-login encryption inspection and the two authentication attempts. Constants `TDS_ENCRYPT_REQ` and `TDS_ENCRYPT_OFF` are used to decide whether CBT can be meaningfully tested.

The main block uses `argparse`, `logger.init()`, `parse_target()`, password prompting, `-target-ip` override, and `-aesKey` forcing Kerberos.

## Control Flow
After parsing arguments, the script resolves domain/user/password/target and initializes logging. `run()` first opens a TDS connection and calls `preLogin()`. If encryption is neither required nor off according to the script's check, it concludes channel binding is off and exits early. Otherwise it performs a normal login with `cbt=None`, records success or failure, then creates a separate connection and retries with `cbt=b''`. The result matrix is interpreted as not enforced, enforced, or invalid credentials.

## State and Persistence
The tool keeps only in-memory option and credential state. It creates short-lived network connections and disconnects after each attempt. It does not write files, change server configuration, or cache authentication material.

## Dependencies and Integration Points
The script depends on Impacket's TDS implementation, including CBT-aware login paths. It integrates with MSSQL over TCP, NTLM or Kerberos authentication, optional domain controller resolution via `-dc-ip`, and optional credential cache use with `-k`.

## Risks
The decision logic is heuristic: if both logins fail, it reports invalid credentials but cannot distinguish all transport, TLS, SPN, or policy failures. The encryption pre-login branch has a terse condition and message that can be confusing because CBT only applies to TLS-protected authentication. The script catches broad exceptions and only exposes details at debug level. It may lock accounts if repeatedly run with bad credentials.

## Test Signals
Tests should cover `_login()` argument routing for Kerberos and NTLM, password prompting conditions, target IP override, and the three result classifications. Integration validation needs MSSQL instances with CBT disabled and enforced, valid and invalid credentials, Kerberos and NTLM authentication, and debug traces for pre-login failures.
