# File Research: sources/local-fs/xfsdump/release.sh

Bash release automation script for xfsdump.

Modes/options:
- `--kup` uploads final tarball/signature with `kup`.
- `--no-commit` skips release commit/tag.
- `--last-head` identifies previous release commit for announcement email content.
- `--for-next` prepares for-next branch announcement instructions.
- `--help` prints usage.

Release flow:
- Optionally edits `VERSION`.
- Sources `./VERSION` and computes `version`.
- Updates `doc/CHANGES`, `configure.ac`, and `debian/changelog`.
- Shows diff, prompts for confirmation, commits with signoff, and creates signed annotated tag.
- Runs `make realclean`, removes old tar/signature files, runs `make dist`.
- Creates uncompressed tar copy, signs it with GPG, verifies signature, renames `.asc` to `.sign`.
- Optionally uploads with `kup`.
- Generates announcement mail template using git log, shortlog, diffstat, and contributor script.

Risks/assumptions:
- Mutates working tree and requires clean-enough git state.
- Requires `$EDITOR`, `gpg`, `make`, `git`, `less`, optional `kup`, and optional `neomutt`.
- Uses `set -e`, but interactive commands and external editor behavior remain manual.
