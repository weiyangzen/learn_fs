<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-migrate-home -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-migrate-home

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-migrate-home_research.md`. Source lines read for this pass: 206.

## Purpose
Root-only migration script that converts an existing user home into an encrypted eCryptfs home by moving the cleartext tree aside, bootstrapping eCryptfs configuration, copying data back through the encrypted mount, and leaving recovery instructions.

## Important APIs, Types, And Functions
Shell functions `usage`, `error`, `warning`, `info`, `assert_dir_empty`, `get_user_home`, `sanity_check`, and `encrypt_dir`; CLI accepts `-u|--user`.

## Control Flow
Validates root privileges, gets the target home from passwd, checks that eCryptfs state does not already exist, requires `rsync` and `lsof`, checks 2.5x free space, ensures destination directories are empty, moves the original home to `/home/$USER.XXXXXXXX`, runs `ecryptfs-setup-private -b`, rsyncs data into the new encrypted home, unmounts it, and prints mandatory login/backup notes.

## State And Persistence Behavior
Creates `/home/.ecryptfs/$USER`, symlinks in the user home via setup-private, a temporary cleartext backup home, and encrypted home contents.

## Dependencies And Integration Points
Depends on root, `getent`, `du`, `df`, `rsync`, `lsof`, `mktemp`, `ecryptfs-setup-private`, `umount`, and conventional `/home` layout.

## Risks And Edge Cases
High blast radius: moving homes and rsyncing data can lock users out or lose data if interrupted. Unquoted passphrase forwarding in setup arguments and open-file/disk-space checks deserve caution.

## Test Signals
Best tested in a disposable VM with a throwaway user, confirming login before reboot and verifying the cleartext backup can restore the original home.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-migrate-home -->
