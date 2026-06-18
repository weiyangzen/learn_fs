# sources/sync-backup/bup/test/lib/btl.sh

Purpose: shell helper library for bup tests, focused on extracting Git tree object IDs, displaying file contents in logs, and capturing stdout/stderr while preserving wrapped command exit status.

Important APIs/types/functions: `btl-ent-oid`, `btl-display-file`, `out-to`, `err-to`, and `both-to`.

Control flow: `btl-ent-oid()` accepts either stdin or one argument, rejects other arities with status 2, trims a `git ls-tree` line at the tab, then emits the final space-delimited field as the object ID. `btl-display-file()` prints quoted delimiters around `cat` output. `out-to()` tees stdout to a file and returns the command status via `PIPESTATUS[0]`. `err-to()` uses dynamic file descriptors to tee stderr while preserving stdout and command status. `both-to()` composes `err-to` and `out-to`.

State and persistence behavior: writes capture files passed by the caller and emits diagnostic content to stdout/stderr. It intentionally supports unknown `set +e` and `pipefail` states.

Dependencies/integration points: intended for shell tests using WVPASS/WVFAIL wrappers where shell redirection around the wrapper would capture the wrong command. It relies on bash features such as `local`, `$'...'`, arrays/`PIPESTATUS`, and dynamic file descriptors.

Risks and test signals: status preservation is the critical behavior; mistakes can produce false passing tests. `err-to()` is the most delicate function because descriptor ordering determines whether stdout and stderr remain separated.
