# sources/test-tools/strace/src/quota.c

Purpose: Decodes `quotactl` and `quotactl_fd` command arguments and quota data structures, including classic and XFS quota interfaces.

Important APIs/types/functions: `SYS_FUNC(quotactl)`, `SYS_FUNC(quotactl_fd)`, `decode_cmd_data`, `print_qcmd`, and struct definitions `if_dqblk`, `if_nextdqblk`, `if_dqinfo`.

Control flow: command words are split into command and quota type. Entry prints operation and special path/fd; `decode_cmd_data` dispatches by quota subcommand and phase, delaying output-only structures until exit. It decodes quota on paths, quota records, next quota records, XFS disk quota, format, info, quota stat/statv, quota flags, and default raw id/address cases.

State and persistence: stateless; uses syscall phase and return status only.

Dependencies/integration: `<linux/dqblk_xfs.h>`, xlat tables for quota commands/types/formats/flags, fetch helpers including `fetch_struct_quotastat`, UID/path/fd printers.

Risks: structures have alignment/padding hazards, noted by packed `if_dqblk` for 32-bit tracees. Abbrev mode intentionally elides long tails. Low 32-bit masking is required on sign-extending architectures such as s390x.

Test signals: classic and XFS quota commands, get vs set phase behavior, fd variant, packed layout on 32-bit personality, abbrev/full output, and unknown command fallback.
