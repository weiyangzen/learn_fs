# File Research: sources/os/bsd/netbsd-src/sys/sys/msg.h

## Purpose
Defines System V message queue ABI, kernel storage structures, sysctl export structures, limits, and syscall/internal entry points.

## Main API
- Public constant: `MSG_NOERROR`.
- Public types: `msgqnum_t`, `msglen_t`.
- Public structure: `struct msqid_ds`.
- NetBSD extensions: `struct msginfo`, `struct msgid_ds_sysctl`, `struct msg_sysctl_info`.
- Kernel structures: `struct __msg`, `struct msgmap`, `kmsq_t`.
- Kernel limits: `MSGSSZ`, `MSGSEG`, computed `MSGMAX`, `MSGMNB`, `MSGMNI`, `MSGTQL`.
- ID helpers: `MSQID`, `MSQID_IX`, `MSQID_SEQ`.
- Userland calls: `msgctl`, `msgget`, `msgsnd`, `msgrcv`.
- Kernel calls: `msginit`, `msgfini`, `msgctl1`, `msgsnd1`, `msgrcv1`.

## Dependencies
Depends on `sys/ipc.h`; kernel sections also use mutexes and condition variables.

## Risks and Notes
The segment size must be a valid power-of-two range checked by implementation code. `struct msqid_ds` contains private implementation fields, so ABI users should treat them as opaque despite header visibility.
