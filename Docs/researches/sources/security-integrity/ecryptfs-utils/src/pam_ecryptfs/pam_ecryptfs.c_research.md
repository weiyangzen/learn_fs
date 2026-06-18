<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/pam_ecryptfs/pam_ecryptfs.c -->
# sources/security-integrity/ecryptfs-utils/src/pam_ecryptfs/pam_ecryptfs.c

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/pam_ecryptfs/pam_ecryptfs.c_research.md`. Source lines read for this pass: 546.

## Purpose
PAM module that loads eCryptfs authentication tokens into the user's session keyring, mounts the user's private directory on session open, unmounts it on close, and rewraps the wrapped mount passphrase when the login password changes.

## Important APIs, Types, And Functions
Exports PAM entry points `pam_sm_authenticate`, `pam_sm_setcred`, `pam_sm_open_session`, `pam_sm_close_session`, and `pam_sm_chauthtok`. Important helpers are `file_exists_dotecryptfs`, `wrap_passphrase_if_necessary`, `fetch_pwd`, and `private_dir`.

## Control Flow
`pam_sm_authenticate` resolves the PAM user, temporarily drops effective credentials to the user, checks `~/.ecryptfs/auto-mount`, skips key loading if already mounted, obtains either `PAM_AUTHTOK` or an independent wrapping passphrase, forks, validates the keyring, and inserts either a raw passphrase token or an unwrapped `wrapped-passphrase` token. Session hooks fork and exec `/sbin/mount.ecryptfs_private` or `/sbin/umount.ecryptfs_private` as the user. `pam_sm_chauthtok` uses old and new PAM tokens to unwrap and rewrap the stored mount passphrase.

## State And Persistence Behavior
Reads and writes `~/.ecryptfs/auto-mount`, `auto-umount`, `wrapping-independent`, `Private.sig`, `wrapped-passphrase`, and `/dev/shm/.ecryptfs-$USER` bootstrap passphrase files. Persists key material only through libecryptfs wrapped-passphrase routines and kernel keyring insertion; it also creates update-notifier marker links for passphrase recording reminders.

## Dependencies And Integration Points
Depends on Linux PAM, libc passwd/group APIs, syslog, setuid/setgid/setgroups, libecryptfs keyring/wrapping APIs, `/sbin/mount.ecryptfs_private`, `/sbin/umount.ecryptfs_private`, and the eCryptfs per-user dotfile layout.

## Risks And Edge Cases
The module handles secrets and privilege transitions; child exit statuses are mostly ignored and PAM often returns success after logging failures. `/dev/shm` bootstrap wrapping, auto-mount markers, and independent wrapping prompts must preserve ownership and mode checks. Any change to UID/GID restoration can break login sessions or leak keys.

## Test Signals
Covered indirectly by private setup/mount scripts and kernel integration tests that require keys, mounts, and unmounts. Manual PAM testing should verify login, logout, password-change rewrap, independent wrapping, and encrypted-home bootstrap paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/pam_ecryptfs/pam_ecryptfs.c -->
