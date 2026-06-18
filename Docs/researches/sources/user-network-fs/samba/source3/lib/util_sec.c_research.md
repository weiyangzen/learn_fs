<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_sec.c -->
# sources/user-network-fs/samba/source3/lib/util_sec.c

## Purpose
`util_sec.c` abstracts Unix credential manipulation for Samba. It records startup credentials, gains/drops root privilege, switches effective IDs, saves/restores real/effective IDs, permanently becomes a user, supports Linux thread-specific credentials, and includes autoconf self-test code for setuid mechanisms.

## Important APIs, types, and functions
Public APIs include `sec_init`, `sec_initial_uid`, `sec_initial_gid`, `root_mode`, `non_root_mode`, `gain_root_privilege`, `gain_root_group_privilege`, `set_effective_uid`, `set_effective_gid`, `save_re_uid`, `restore_re_uid_fromroot`, `restore_re_uid`, `save_re_gid`, `restore_re_gid`, `set_re_uid`, `become_user_permanently`, `set_thread_credentials`, and `is_setuid_root`. Internal `assert_uid` and `assert_gid` panic on failed transitions when running root mode.

## Control flow
`sec_init` captures initial effective UID/GID, with UID wrapper handling for tests. Credential setters compile to the platform-supported mechanism: `setresuid`, `seteuid`, `setreuid`, or `setuidx`. Root gain sets real/effective IDs to zero where possible and asserts success. Effective setters drop only effective identity where supported. Permanent become first regains root, then sets real/effective/saved IDs and group IDs to the target so root cannot be regained. Linux thread credentials reset to root, set primary and supplementary groups, then set target UID, with a thread-local cache to skip repeated identical transitions.

## State and persistence behavior
Process-global state includes initial UID/GID and saved real/effective UID/GID pairs. With Linux thread credentials and `__thread`, each thread caches the last credential set. The code mutates OS process or thread credentials, a high-impact state change.

## Dependencies and integration points
It depends on Samba setid wrappers, uid-wrapper test integration, platform configure macros, and privilege-changing callers throughout smbd/winbindd/VFS code.

## Risks and edge cases
Credential code is security critical and platform-dependent. Assertions intentionally panic in root mode when requested IDs do not take effect. Non-root mode suppresses some panics to support tests and non-root smbd. Thread-credential caching assumes the gidset pointer identity is a valid cache key; mutated group arrays at the same address would be risky.

## Test signals
The `AUTOCONF_TEST` main exercises selected platform setid calls. Runtime tests should verify root/non-root mode, save/restore pairs, permanent drop irreversibility, Linux thread credential group setting, uid-wrapper behavior, and EAGAIN handling for per-user process limits.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_sec.c -->
