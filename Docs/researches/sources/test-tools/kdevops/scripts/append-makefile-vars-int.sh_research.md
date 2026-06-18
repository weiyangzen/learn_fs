# sources/test-tools/kdevops/scripts/append-makefile-vars-int.sh

Purpose: concatenates command-line arguments into a single integer-like Make/Kconfig string, defaulting to `0`.

Important APIs/types/functions: Bash loop over positional arguments and `echo`.

Control flow: prints `0` for no args; otherwise appends all non-empty argument strings and prints the result.

State/persistence behavior: stateless stdout helper.

Dependencies/integration: used from Make/Kconfig variable composition.

Risks/test signals: arguments are concatenated without separators or validation. Test signal is expected stdout for empty and multi-argument cases.
