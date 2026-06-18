# File Research: sources/os/linux/linux/fs/quota/kqid.c

Small helper file for kernel quota identifiers, `struct kqid`.

Key responsibilities:
- `qid_eq()` compares quota identifiers, dispatching by quota type to UID, GID, or project-ID comparison.
- `qid_lt()` provides ordering first by quota type, then by typed ID.
- `from_kqid()` maps a kernel quota ID into a user namespace, returning `(qid_t)-1` on unmapped IDs.
- `from_kqid_munged()` maps with overflow fallback, guaranteeing a printable/user-visible ID.
- `qid_valid()` validates the typed ID payload.

Supported quota types:
- `USRQUOTA`: uses `kuid_t`.
- `GRPQUOTA`: uses `kgid_t`.
- `PRJQUOTA`: uses `kprojid_t`.

Research notes:
- Invalid quota types call `BUG()`, so callers must validate `qid.type`.
- These helpers are exported and used by quota core, netlink warning emission, and on-disk quota format code.
