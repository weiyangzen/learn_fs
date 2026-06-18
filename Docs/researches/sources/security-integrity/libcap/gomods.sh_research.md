## sources/security-integrity/libcap/gomods.sh

Purpose: bulk helper for updating libcap Go module dependency versions in all `go.mod` files under the current tree.

Important APIs/functions: version argument, `find . -name 'go.mod'`, and `sed -i` replacement.

Control flow: requires a target version argument, otherwise prints usage and exits 1; for each `go.mod`, rewrites lines beginning with `kernel.org/... v...` to the requested version.

State/persistence: edits every discovered `go.mod` in place.

Dependencies/integration: Bash, find, GNU/BSD-compatible `sed -i` behavior. Used for release/version maintenance.

Risks: broad regex can rewrite unintended `kernel.org` module lines; no dry run or git check; `sed -i` portability varies.

Test signals: run on a disposable tree, inspect `git diff`, and validate `go mod tidy/test`.
