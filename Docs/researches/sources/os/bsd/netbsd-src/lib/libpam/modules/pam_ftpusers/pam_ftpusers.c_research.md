# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_ftpusers/pam_ftpusers.c

Account module that checks `/etc/ftpusers`. It resolves the PAM user, scans non-comment entries, matches literal usernames, and supports `@group` entries by resolving group membership.

By default, a found entry allows access and a missing entry denies; the `disallow` option inverts that behavior. File-open failures are logged and then evaluated as not found.
