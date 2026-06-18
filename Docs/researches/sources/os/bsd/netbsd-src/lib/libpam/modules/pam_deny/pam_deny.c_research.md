# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_deny/pam_deny.c

PAM module that deliberately denies access. Authentication obtains the user then returns `PAM_AUTH_ERR`; setcred returns `PAM_CRED_ERR`; account returns `PAM_AUTH_ERR`; session open/close return `PAM_SESSION_ERR`.

Password change returns `PAM_AUTHTOK_ERR`, except `PAM_PRELIM_CHECK` can return `PAM_IGNORE` when `prelim_ignore` is configured. Unknown password options are syslogged.
