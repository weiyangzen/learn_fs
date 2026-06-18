## sources/security-integrity/libcap/doc/crosslink.sh

Purpose: helper script for auditing manpage `.so man...` cross-reference redirect pages against their targets.

Important APIs/functions: shell loop over `*.?`, `grep -F '.so m'`, `awk`, and `sed`.

Control flow: for each one-character-extension manpage, extracts the redirect target from `.so man...`, skips non-redirect pages, prints a divider and mapping, then greps the target page for the source basename.

State/persistence: no writes.

Dependencies/integration: intended to be run from `doc/`; assumes manpage redirect syntax and local target files. Supports documentation maintenance rather than build output.

Risks: only handles simple `*.?` section names and fixed `.so m` text; grep failures are informational, not machine-enforced.

Test signals: run after adding or renaming manpage redirect files and inspect missing references.
