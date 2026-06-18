# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/hppa/sys/compat_sigpending.S

## Scope

HPPA compatibility implementation of old `sigpending`.

## Behavior

- Defines explicit `ENTRY(sigpending, 0)`.
- Calls compatibility syscall and stores the returned old mask through the caller pointer.

## Dependencies And Invariants

- Must obey HPPA register and return-value convention while adapting old signal mask ABI.
