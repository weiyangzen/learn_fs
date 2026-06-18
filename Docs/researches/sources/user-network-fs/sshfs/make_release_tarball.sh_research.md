# sources/user-network-fs/sshfs/make_release_tarball.sh

Purpose: release helper that creates and signs an `sshfs-3*` source tarball from a Git tag.

Important APIs/types/functions: chooses latest matching tag unless an argument is provided, creates a directory, extracts `git archive`, deletes `.gitignore`, removes release-excluded CI/helper files, creates an xz tarball, signs it with GPG, and prints contributor names since the previous merged tag.

Control flow: `set -e` aborts on errors; tag selection branch; archive/exclusion/signing; previous tag lookup and `git log` summary.

State and persistence behavior: creates `${TAG}/`, `${TAG}.tar.xz`, and detached signature in the current directory.

Dependencies and integration points: Git tags, tar with xz support, GPG, and historical Travis scripts.

Risks: existing output directory causes failure. It removes fixed files that may not exist in newer trees. Tag lookup depends on tag naming/merge history.

Test signals: dry-run in a clean clone, expected tarball contents, valid GPG signature, and contributor range correctness.
