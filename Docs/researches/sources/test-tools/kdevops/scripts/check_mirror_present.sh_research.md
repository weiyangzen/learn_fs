# sources/test-tools/kdevops/scripts/check_mirror_present.sh

Purpose: reports whether a supplied mirror directory exists.

Important APIs/types/functions: single directory test and `echo y/n`.

Control flow: prints `y` when `$1` is a directory, else `n`.

State/persistence behavior: read-only.

Dependencies/integration: generic Kconfig/Make mirror presence helper.

Risks/test signals: unquoted path can break on spaces. Test signal is expected `y/n`.
