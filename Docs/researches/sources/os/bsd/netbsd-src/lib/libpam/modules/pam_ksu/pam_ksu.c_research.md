# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_ksu/pam_ksu.c

Read completely: 293 lines.

This module authenticates `su`-style access using Kerberos. It determines a Kerberos principal for the invoking user, checks whether that principal is allowed to become the target user via `krb5_kuserok`, and then authenticates the principal with a password and verifies initial credentials against a local keytab.

Important behavior: when target user is `root`, `get_su_principal` transforms the current/default principal into a root instance such as `user/root@REALM`; otherwise it uses the current/default principal. It temporarily switches effective uid to the real uid while locating the default ccache. It disables Heimdal home-directory access while deriving credentials, then briefly enables it only for the `.k5login` `krb5_kuserok` check.

`auth_krb5` allocates get-init-creds options, prompts for the target principal password, gets initial credentials, and verifies them with `krb5_verify_init_creds` with `ap_req_nofail` set.

Security/reliability notes: authentication requires a usable local keytab. There are memory leaks on some early returns in `auth_krb5` because allocated options are not freed on all paths, but the PAM process lifetime may limit impact.
