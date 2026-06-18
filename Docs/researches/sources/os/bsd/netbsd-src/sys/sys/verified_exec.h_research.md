# File Research: sources/os/bsd/netbsd-src/sys/sys/verified_exec.h

Read completely: 112 lines.

Defines Veriexec flags, ioctl interface, modes, status values, and kernel hooks.

Key elements:
- Entry flags distinguish direct execution, indirect interpreter execution, plain file opens, and untrusted storage.
- Pseudo-device ioctls support load, table size, delete, query, dump, and flush operations using property-list references.
- Strict modes include learning, IDS, IPS, and lockdown.
- Fingerprint status values distinguish not evaluated, valid, and mismatch.
- Page fingerprint status values cover none, ready, and failure.
- Kernel declarations cover fingerprint algorithm registration, file add/delete, verification, lookup, table delete, conversion, dump, flush, vnode purge, remove/rename/unmount/open checks.

Risks and notes:
- Security-sensitive: incorrect verification or vnode lifecycle handling can bypass execution policy.
- Ioctl/property-list ABI must match userland Veriexec tooling.
