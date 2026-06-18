## sources/security-integrity/libcap/kdebug/test-bash.sh

Purpose: wrapper that satisfies scripts expecting `/bin/bash` in the initramfs while actually invoking `/bin/sh`.

Important APIs/functions: `exec sh "$@"`.

Control flow: replaces itself with `sh` and forwards all arguments.

State/persistence: none.

Dependencies/integration: busybox or shell available as `sh`; included in `test-kernel.sh` initramfs as `/bin/bash`.

Risks: scripts using bash-specific syntax will fail because this is only a compatibility shim.

Test signals: initramfs quicktest scripts that reference bash still execute when POSIX-compatible.
