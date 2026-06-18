# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_afslog/pam_afslog.c

PAM module for AFS token management from Kerberos credentials. Authentication returns `PAM_IGNORE`; all functional behavior is in `pam_sm_setcred`.

It initializes a Kerberos context, opens the ccache from `KRB5CCNAME` or the default, reads the principal, consults appdefault `afslog`, and if enabled and AFS is present establishes a PAG and calls `krb5_afslog` for establish/reinitialize/refresh, or `k_unlog` for delete credentials.
