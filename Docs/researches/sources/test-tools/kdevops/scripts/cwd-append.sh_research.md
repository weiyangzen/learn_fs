<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/cwd-append.sh -->
# sources/test-tools/kdevops/scripts/cwd-append.sh

Purpose: prints the current working directory joined with its first argument. It is used as a tiny Kconfig helper for defaults such as appending `kdevops` to the current path.

Important APIs and functions: no functions; it executes `echo $(pwd)/$1`.

Control flow: linear startup, calls `pwd`, interpolates `$1`, prints one line, exits with the shell status from `echo`.

State and persistence: no persistent state; reads the process working directory and the first positional argument only.

Dependencies and integration: uses `/bin/bash` and `pwd`. The observed integration point is `kconfigs/Kconfig.libvirt`, where it provides a default custom libvirt storage pool path.

Risks: the argument is unquoted, so whitespace, glob characters, or empty values can produce surprising output. The command substitution is unnecessary and also unquoted. Test signals are simple shell tests from directories with spaces and without an argument to confirm expected Kconfig-safe behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/cwd-append.sh -->
