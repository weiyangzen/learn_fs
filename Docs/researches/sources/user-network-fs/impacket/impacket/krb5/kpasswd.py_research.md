# sources/user-network-fs/impacket/impacket/krb5/kpasswd.py

Purpose: implements Microsoft/Windows Kerberos change-password and set-password protocol behavior over kpasswd TCP/464 using RFC 3244-style AP_REQ plus KRB_PRIV messages.

Important APIs/types: constants define port, protocol version, and `kadmin/changepw` SPN. `KPasswdResultCodes`, `RESULT_MESSAGES`, `PasswordPolicyFlags`, and `_decodePasswordPolicy()` interpret server results. `ChangePasswdData` is the ASN.1 payload. `createKPasswdRequest()` builds authenticator, AP_REQ, encrypted change data, KRB_PRIV, and packet header. `decodeKPasswdReply()` parses AP_REP/KRB_PRIV and returns success/result/message. `changePassword()` delegates to `setPassword()`, which acquires a changepw TGT, builds the request, sends it, and raises `KPasswdError` on failure.

Control flow and persistence: `setPassword()` optionally loads a changepw TGT from `KRB5CCNAME`, otherwise calls `getKerberosTGT()` with serverName `kadmin/changepw`. It decodes the ticket, generates a subkey if not supplied, sends the kpasswd request via `sendReceive()`, and decodes the response. There is no file write; only optional cache read.

Dependencies and integration: uses Kerberos ASN.1 helpers, `CCache`, `crypto.Key`, random bytes, `types.Principal/Ticket/KerberosTime`, and `kerberosv5.sendReceive/getKerberosTGT`. It is a credential-changing integration point for Impacket tools.

Risks and test signals: the cleartext new password is embedded before encryption, so debug logs around base64 payloads are sensitive. `decodeKPasswdReply()` ignores AP_REP cryptographic validation and focuses on KRB_PRIV decryption. Password policy parsing expects an AD-specific binary layout. Tests should cover request construction with deterministic `now`/sequence/subkey, target-user set-password fields, cache TGT selection, result-code mapping, policy decoding, malformed reply handling, and failed decrypt handling.
