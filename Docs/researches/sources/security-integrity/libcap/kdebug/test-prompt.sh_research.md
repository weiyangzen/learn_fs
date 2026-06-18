## sources/security-integrity/libcap/kdebug/test-prompt.sh

Purpose: tiny prompt helper for the kdebug initramfs shell.

Important APIs/functions: prints `$(pwd)# ` without a newline.

Control flow: immediate echo.

State/persistence: none.

Dependencies/integration: installed as `/bin/myprompt` in the generated initramfs.

Risks: assumes POSIX `pwd` and shell command substitution; no escaping.

Test signals: interactive kdebug shell displays current directory prompt.
