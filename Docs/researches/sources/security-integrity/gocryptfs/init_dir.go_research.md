# sources/security-integrity/gocryptfs/init_dir.go

Purpose: This file implements `gocryptfs -init` for forward and reverse mode filesystem initialization.

Important APIs and functions: `isEmptyDir` verifies an existing empty directory, `isDir` validates reverse-mode source directories, and `initDir(args)` creates config files and forward-mode `gocryptfs.diriv` as needed.

Control flow and state: Forward mode requires an empty cipherdir, obtains/generates credentials, creates `gocryptfs.conf`, writes initial directory IV when names are encrypted, and handles custom config paths. Reverse mode uses `.gocryptfs.reverse.conf` next to plaintext data and does not require emptiness.

Dependencies and integration points: Integrates CLI args, password/master-key/FIDO2 handling, `configfile.Create`, name encryption diriv generation, and logging.

Risks and test signals: Initialization persists the root trust/config state, so partial failures and unsafe directory selection are high-risk. Signals include created config permissions, correct feature flags, diriv presence/absence, and refusal to initialize nonempty forward dirs.
