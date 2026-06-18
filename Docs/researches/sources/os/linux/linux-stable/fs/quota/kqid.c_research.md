# File Research: sources/os/linux/linux-stable/fs/quota/kqid.c

## Purpose
Provides exported helper operations for kernel quota identifiers, abstracting over user, group, and project quota ID types.

## Key Functions
- `qid_eq()`: compares two `struct kqid` values by type and then by uid/gid/projid equality.
- `qid_lt()`: total ordering helper across quota type and typed ID value.
- `from_kqid()`: maps a kernel quota ID into a target user namespace, returning `(qid_t)-1` if unmapped.
- `from_kqid_munged()`: maps a kernel quota ID into a target namespace, returning overflow IDs rather than failure.
- `qid_valid()`: checks type-specific validity.

## Dependencies
Uses Linux namespace ID helpers: `from_kuid`, `from_kgid`, `from_kprojid`, and munged/valid/equality variants.

## Notes
All helpers switch on `USRQUOTA`, `GRPQUOTA`, and `PRJQUOTA`; invalid types hit `BUG()`, reflecting that callers must pass a valid quota type.
