# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/common/makefile

- Role: Unix-style makefile to build `common.a`.
- Inputs: `mail.o`, `aux.o`, `string.o`, and `${SYSOBJ}`.
- Targets: Archive creation with `ar`, optional `ranlib`, and `clean`.
- Risks/notes: Mentions dependencies such as `aux.h`, `string.h`, and `mail.h` that are not part of this grouped file list.
