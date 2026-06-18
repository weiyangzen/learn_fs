# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_self/pam_self.c

Read completely: 97 lines.

This module authenticates when the real uid matches the target account’s uid. It fetches `PAM_USER`, resolves the passwd entry, denies real uid 0 unless `allow_root` is configured, and succeeds only on uid equality.

`pam_sm_setcred` is a no-op success path.

Security/reliability notes: this is identity-continuity authorization, not password authentication. It uses real uid to avoid effective-uid privilege confusion.
