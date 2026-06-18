# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_krb5/pam_krb5.c

Read completely: 1135 lines.

This is a full Kerberos 5 PAM module implementing authentication, credential establishment, account checks, and password changes. It uses Heimdal by default (`COMPAT_HEIMDAL`) and has compatibility shims for MIT Kerberos guarded by macros.

Authentication flow: `pam_sm_authenticate` gets `PAM_USER`, `PAM_RUSER`, and `PAM_SERVICE`, initializes a Kerberos context, verifies that a local service key exists unless `allow_kdc_spoof` is configured, allocates initial-credential options, applies `forwardable` and `renewable` options, parses the principal, gets the password token, optionally maps realm-qualified names to local users, fetches a TGT with `krb5_get_init_creds_password`, stores it in a temporary memory ccache, verifies the TGT against the local keytab, and saves the ccache name as PAM data with `cleanup_cache`.

Credential flow: `pam_sm_setcred` copies the temporary ccache into a persistent ccache unless `no_ccache` is set. It supports refresh/reinitialize using `KRB5CCNAME`, or establishment using the `ccache` option with `%u` and `%p` substitution, defaulting to `FILE:/tmp/krb5cc_<uid>`. It temporarily drops effective gid/uid to the target user before resolving or creating the persistent cache, copies credentials, fixes ownership/mode for file caches, and sets `KRB5CCNAME`.

Account flow: `pam_sm_acct_mgmt` resolves the temporary ccache and checks `krb5_kuserok` against `PAM_USER`. If no Kerberos ccache was established, it returns success and lets authentication stack ordering decide policy.

Password flow: `pam_sm_chauthtok` handles prelim as success and update by getting old credentials for `kadmin/changepw`, prompting for a new password, calling `krb5_set_password`, and reporting Kerberos password-change result messages.

Helper functions: `verify_krb_v5_tgt_begin` searches keytab service principals, preferring `host/<host>` and falling back to the PAM service principal; `verify_krb_v5_tgt` builds and reads an AP request against the chosen local service key; `cleanup_cache` destroys the temporary ccache at `pam_end`; `log_krb5` formats Kerberos errors to PAM/syslog logging.

Security/reliability notes: the module explicitly defends against spoofed KDCs by requiring local keytab verification unless `allow_kdc_spoof` is configured. Credential-cache handling drops privileges before file creation, but failures before credential restoration still flow through cleanup that restores euid/egid. `asprintf` results for the principal are not checked before `krb5_parse_name`, so out-of-memory behavior depends on downstream tolerance.
