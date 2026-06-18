<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-mount-private -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-mount-private

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-mount-private_research.md`. Source lines read for this pass: 81.

## Purpose
Interactive shell wrapper for mounting a user's configured private directory when the required mount key is not already in the keyring.

## Important APIs, Types, And Functions
Uses `~/.ecryptfs/wrapping-independent`, `wrapped-passphrase`, `Private.sig`, `ecryptfs-unwrap-passphrase`, `ecryptfs-add-passphrase`, `ecryptfs-insert-wrapped-passphrase-into-keyring`, and `/sbin/mount.ecryptfs_private`.

## Control Flow
First silently tries `/sbin/mount.ecryptfs_private`. If that fails and config files exist, prompts up to three times for the login or independent wrapping passphrase, inserts the FEK or FEK/FNEK keys, then invokes the setuid mount helper.

## State And Persistence Behavior
Reads per-user dotfiles and modifies only kernel keyring/mount state. It may print a current-shell directory refresh hint if `$PWD` is the mounted directory.

## Dependencies And Integration Points
Depends on shell, stty, gettext, head, wc, configured eCryptfs files, and installed helper binaries.

## Risks And Edge Cases
Passphrase handling through pipelines is sensitive; stdin mode must preserve NUL/newline behavior. The one-line versus two-line signature file controls whether filename encryption key insertion is attempted.

## Test Signals
Covered by setup-private's mount/write/umount/read sanity flow and manual login/private-directory mount tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-mount-private -->
