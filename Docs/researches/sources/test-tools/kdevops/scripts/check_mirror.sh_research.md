# sources/test-tools/kdevops/scripts/check_mirror.sh

Purpose: Kconfig helper for local Linux mirror availability under `/mirror/`.

Important APIs/types/functions: directory check, `ls -1 | wc -l`, and symbol-specific responses.

Control flow: if `/mirror/` exists, answers enable, use, or first-run install depending on requested symbol and directory content; otherwise prints `n`.

State/persistence behavior: read-only filesystem inspection.

Dependencies/integration: used by local Linux mirror Kconfig options.

Risks/test signals: hard-coded path and unquoted variables; `INSTALL_LOCAL_LINUX_MIRROR` emits `KDEVOPS_FIRST_RUN` rather than `y`. Test signals are expected Kconfig stdout for empty/non-empty mirror directories.
