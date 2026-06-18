# sources/test-tools/strace/src/linux/generic/errnoent.h

Purpose: maps `generic` errno numbers to symbolic names, with 148 named errno slots such as EPERM, ENOENT, ESRCH, EINTR, EIO, ENXIO, E2BIG, ENOEXEC.

Important APIs/types/functions: string table entries indexed by numeric errno; there are no functions.

Control flow: syscall-exit decoding converts an architecture-specific error number into the indexed name for printing.

State/persistence behavior: static lookup metadata only.

Dependencies/integration: consumed by strace xlat/table-generation code; includes no additional headers.

Risks/test signals: architecture-specific errno numbering differs from generic Linux; validate by comparing against the arch UAPI errno header and tracing syscalls returning nonportable errors.

Source-read signal: reviewed complete local file (155 lines).
