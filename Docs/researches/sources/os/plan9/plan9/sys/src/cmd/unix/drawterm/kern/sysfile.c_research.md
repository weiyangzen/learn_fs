# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/sysfile.c

This file implements drawterm's hosted Plan 9 file, namespace, descriptor, error-string, and rendezvous syscall layer.

Key behavior:
- Descriptor management: `growfd`, `findfreefd`, `newfd`, `newfd2`, `fdtochan`, `fdclose`.
- File syscalls: open/create/close/dup/pipe/read/pread/write/pwrite/seek/stat/fstat/wstat/fwstat/remove/chdir.
- Namespace syscalls: `bindmount`, `_sysbind`, `_sysmount`, `_sysunmount`.
- Public wrappers convert `waserror` exceptions into `-1` returns and swap `errstr`/`syserrstr`.
- Error APIs: `werrstr`, `__errfmt`, `errstr`, `rerrstr`.
- `_sysrendezvous`/`sysrendezvous` implement Plan 9 rendezvous value exchange by tag.

Important details:
- File-descriptor tables grow by `DELTAFD` but cap around 5000 descriptors.
- `kread` supports union directory reads through `unionread`, advancing mounted union elements when one returns no data.
- `kwrite` reserves channel offset before writing and rolls it back on partial writes/errors.
- `validstat` checks packed 9P stat buffers and validates rewritten names.
- `bindmount` handles both bind and mount paths, including mount device attach with optional auth channel.
- The code contains visible duplicated lines in `_syspipe`, `_sysseek`, and `syschdir`, but semantics are mostly unaffected because the duplicates repeat checks/returns.
