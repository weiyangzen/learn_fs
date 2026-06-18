<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-verify -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-verify

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-verify_research.md`. Source lines read for this pass: 245.

## Purpose
Validation script for checking whether a user's encrypted home/private setup and filename-encryption mode match expected configuration.

## Important APIs, Types, And Functions
Functions include `ecryptfs_exists`, `sigfile_valid`, `mountfile_valid`, `automount_true`, `owns_mountpoint`, `mount_is_home`, `mount_is_private`, `filenames_encrypted`, and `filenames_not_encrypted`. CLI options are additive.

## Control Flow
Parses requested checks and optional `--user`, resolves home, then executes each check. Any failure prints an error and exits nonzero; all checks passing prints configuration valid.

## State And Persistence Behavior
Read-only over passwd data, `~/.ecryptfs`, `Private.sig`, `Private.mnt`, mountpoint ownership, and automount flags.

## Dependencies And Integration Points
Depends on shell, gettext, getent, stat, wc, and the standard eCryptfs per-user layout.

## Risks And Edge Cases
Assumes fixed file names and one/two-line signature semantics. It checks configuration, not whether keys are available or mounts are currently usable.

## Test Signals
Use after setup-private and encrypted-home bootstrap with `--home`, `--private`, `--filenames-encrypted`, and `--filenames-not-encrypted` combinations.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-verify -->
