<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-recover-private -->
# sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-recover-private

Final split target: `Docs/researches/sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-recover-private_research.md`. Source lines read for this pass: 120.

## Purpose
Root-only recovery helper that discovers `.Private` directories and mounts them read-only by default using either the wrapped passphrase or the recorded mount passphrase.

## Important APIs, Types, And Functions
Shell functions `error` and `info`; CLI accepts optional `--rw` and optional target directories.

## Control Flow
Requires root, discovers candidate directories by arguments or `find / -type d -name .Private`, prompts per candidate, detects filename encryption, inserts keys from `wrapped-passphrase` or direct mount passphrase, builds eCryptfs mount options, validates keys with `keyctl`, creates `/tmp/ecryptfs.XXXXXXXX`, and mounts with `mount -i -t ecryptfs`.

## State And Persistence Behavior
Creates temporary recovery mountpoints and inserts keys into the user keyring; does not alter the encrypted source unless `--rw` is used and the user writes through the mount.

## Dependencies And Integration Points
Depends on root, find, keyctl, mount, mktemp, eCryptfs passphrase tools, and the `Private.sig`/`wrapped-passphrase` layout.

## Risks And Edge Cases
`find /` is expensive and noisy; `keyctl` check on an empty FNEK string can be brittle. Recovery mounts should default to read-only to avoid damaging partially recovered data.

## Test Signals
Manual recovery test should use a copied `.Private` tree and both wrapped-passphrase and mount-passphrase paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/utils/ecryptfs-recover-private -->
