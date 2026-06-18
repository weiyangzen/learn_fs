# sources/storage-engines/badger/changes.sh

Purpose: generates a release/change description from git log entries and rewrites issue references to fully qualified GitHub links.

Important flow: Bash script with `set -e` reads `GHORG` and `GHREPO` defaults, prints a preamble containing the script source and invocation, then runs `git log --oneline --reverse "$@"` and pipes through two `sed` expressions: one removes short hashes, the other rewrites `#123`-style references to `org/repo#123`.

State and persistence: writes only to stdout. Dependencies are Bash, git, sed, and a Git history range supplied by arguments. Risks: embedding the whole script in output is verbose, issue-reference regex may rewrite patterns in unintended contexts, and unquoted `${@:1}` in the invocation display can misrepresent arguments with spaces. Test signals are sample git ranges, issue-reference rewrite checks, and shellcheck/shfmt.
