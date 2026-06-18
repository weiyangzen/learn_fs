# sources/test-tools/kdevops/scripts/check_file_empty.sh

Purpose: ensures a file exists and reports whether it is non-empty.

Important APIs/types/functions: `mkdir --parents $(dirname $FILE)`, `touch`, `test -s`, and `echo y/n`.

Control flow: creates parent directory and file when missing, prints `y` if file has size, otherwise `n`.

State/persistence behavior: creates directories/files as a side effect.

Dependencies/integration: Kconfig/Make helper for generated or sentinel files.

Risks/test signals: unquoted paths break on spaces and the helper is not read-only despite its name. Test signal is file existence and correct `y/n` output.
