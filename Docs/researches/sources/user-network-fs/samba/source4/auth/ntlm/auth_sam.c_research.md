<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_sam.c -->
# sources/user-network-fs/samba/source4/auth/ntlm/auth_sam.c

Purpose: implements local SAM-backed NTLM authentication backends `sam` and `sam_ignoredomain`, including password validation, account policy checks, bad-password accounting, protected-user restrictions, authentication policy enforcement, RODC replication triggers, and previous-password grace behavior.

Important APIs: `authsam_password_ok()` validates plaintext/hash/response credentials against NT hashes or AES256 Kerberos supplemental credentials. `authsam_password_check_and_record()` obtains current and historical secrets, checks lockout, tries previous passwords within policy windows, updates badPwdCount, and sets non-authoritative on RODC. `authsam_authenticate()` applies interactive restrictions, authentication policies, password checks, netlogon trust server policy, account restrictions, and success accounting. `authsam_check_password_internals()` resolves UPNs, searches SAM, builds `auth_user_info_dc`, rejects Protected Users for NTLM, and attaches session keys. `authsam_want_check()` decides domain ownership and forest routing. `auth4_sam_init()` registers `sam` and `sam_ignoredomain`.

Control flow: the backend first decides whether it owns the mapped domain/account. For AD DC UPNs it may use trust routing and later crack names to NT4 form. It loads the account, creates preliminary user info, enforces Protected Users restrictions, authenticates secrets, updates accounting, reparents audit info, and returns completed user info. Wrong passwords continue into history checks before bad-password updates; successful previous-password network auth can be allowed during configured grace periods.

State and persistence: reads and writes SAM LDB state: password hashes/supplemental credentials, account control, badPwdCount/lockout, logon accounting, and gMSA current time. It may send IRPC messages to winbind or dreplsrv for zero-password and secret-replication handling.

Dependencies and integration: depends on DSDB/SAMDB, NTLM check helpers, Kerberos AES key extraction, GKDI/gMSA utilities, authn policy utilities, winbind/drepl IRPC, roles/trust routing, and auth SAM reply conversion.

Risks and test signals: security-sensitive boundaries include constant-time hash comparisons, hiding invalid historical hashes, Protected Users denying NTLM, smartcard-required behavior, old-password grace, gMSA five-minute skew, RODC non-authoritative fallback, and authentication policy audit info. Tests should cover standalone/member/DC domain matching, UPN cracking, cross-forest rejection, no secrets on RODC, AES-only accounts, bad-password accounting failure, trust account policy, and generated session keys.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_sam.c -->
