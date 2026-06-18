# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_unix/pam_unix.c

Read completely: 632 lines.

This module implements Unix password authentication, account expiry checks, and password changes for local files and optionally NIS.

Authentication: `pam_sm_authenticate` gets the target user or `getlogin()` under `auth_as_self`, obtains the passwd entry, handles empty passwords only when `nullok` is set and `PAM_DISALLOW_NULL_AUTHTOK` is absent, prompts for `PAM_AUTHTOK`, and compares `crypt(pass, realpw)` to the stored hash. Unknown users get dummy authentication against `"*"` to reduce obvious branching.

Account management: `pam_sm_acct_mgmt` checks null password policy, login class lookup, account expiry (`pw_expire`), password expiry (`pw_change`), and warning windows from login class `password-warn`.

Password changes: `pam_sm_chauthtok` chooses `passwd_db` from option, NIS availability, or local files. In prelim mode it verifies old password unless root is changing a local password, and denies non-root changes to root. In update mode it reads login class `minpasswordlen` and `passwordtime`, prompts for a new password with retry handling, rejects very short and all-lowercase passwords on first attempts, generates a salt from password configuration, hashes with `crypt`, sets password expiry, and updates either local master.passwd or NIS.

Local update uses `pw_lock`, opens `_PATH_MASTERPASSWD`, calls `pw_copyx`, and rebuilds the password database with `pw_mkdb`. NIS update finds the master server, ensures `yppasswdd` is on a privileged port, checks caller uid, builds a `yppasswd` RPC structure, and calls `YPPASSWDPROC_UPDATE`.

Security/reliability notes: password quality checks are minimal and partly advisory by retry count. `crypt` return is not checked for null before assignment/comparison. The NIS path uses UDP RPC and legacy trust assumptions, with a privileged-port check as mitigation.
