# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_group/pam_group.c

Authentication module that authorizes a remote/applicant user based on membership in a configured group, defaulting to `wheel`. It checks the target PAM user, optionally ignores non-root targets with `root_only`, then resolves `PAM_RUSER` and group membership by primary gid or member list.

Options include `authenticate` to require the applicant's password, `deny` to invert success/failure for members, and `fail_safe` to treat group lookup problems as success. Password authentication uses `pam_get_authtok`, `crypt`, and verbose failure logging.
