# sources/test-tools/kdevops/playbooks/scripts/workflows/fstests/sort-expunges.sh

Purpose: normalizes fstests expunge `.txt` files by sorting and deduplicating entries in a supplied directory tree.

Important APIs/types/functions: Bash argument parsing, `find $DIR -name *.txt`, symlink skip check, `sort`, `uniq`, and `mv`.

Control flow: validates one argument/help, ensures the argument is a directory, finds text files, skips symlinks, writes sorted unique content to `<file>.tmp`, then replaces the original.

State/persistence behavior: rewrites every non-symlink `.txt` file under the supplied directory.

Dependencies/integration: used by fstests workflow scripts to keep expunge lists stable.

Risks/test signals: unquoted variables can break on spaces; tmp file replacement is not trap-protected. Test signals are sorted unique file contents and unchanged symlinks.
