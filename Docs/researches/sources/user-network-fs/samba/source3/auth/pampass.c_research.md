# sources/user-network-fs/samba/source3/auth/pampass.c

## Purpose
This file implements Samba's PAM integration for plaintext password validation, account checks, session open/close, credential establishment, and password changes. It compiles to no-op account/session stubs when PAM is unavailable.

## Important APIs, Types, and Functions
With `WITH_PAM`, important helpers include `smb_pam_conv`, `smb_pam_passchange_conv`, `make_pw_chat`, `smb_setup_pam_conv`, `smb_pam_start`, `smb_pam_auth`, `smb_pam_account`, `smb_pam_setcred`, `smb_internal_pam_session`, and `smb_pam_chauthtok`. Public functions are `smb_pam_claim_session`, `smb_pam_close_session`, `smb_pam_accountcheck`, `smb_pam_passcheck`, and `smb_pam_passchange`.

## Control Flow
Authentication creates a PAM conversation carrying username/password, starts service `samba`, sets RHOST and TTY when supported, calls `pam_authenticate`, `pam_acct_mgmt`, and `pam_setcred`, maps PAM errors to NTSTATUS, and always ends the PAM handle. Session functions respect `lp_obey_pam_restrictions` and open/close sessions. Password changes build a prompt/reply chat script from `lp_passwd_chat`, substitute username/old/new password tokens, and call `pam_chauthtok`.

## State and Persistence
No long-lived file-local state is stored. PAM modules may update system credential/session/password state. Temporary conversation data is malloc-owned and freed through `smb_pam_end`; password chat nodes are explicitly freed.

## Dependencies and Integration Points
Dependencies include platform PAM headers, Samba PAM error mapping, loadparm options such as `obey pam restrictions`, `null passwords`, and `passwd chat`, string/wildcard helpers, and callers in `pass_check`, `auth.c`, and session management code.

## Risks and Test Signals
Risks include PAM stack differences across OSes, prompt matching failures during password change, memory cleanup on early start failures, null-password policy mismatches, and NTSTATUS/PAM error mapping bugs. Tests should cover PAM auth success/failure, account expired/disabled cases, session claim/close, password change prompt variants, builds without PAM, and configurations with PAM restrictions disabled.
