# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cred_impl.h

## Role

Defines the private credential implementation layout for kernel and kmem consumers.

## Main Structures

- `credgrp_t`:
  - reference count.
  - number of groups.
  - flexible-style group array with one declared element.

- `struct cred`:
  - reference count.
  - effective, real, and saved UID/GID.
  - privilege state.
  - project id.
  - zone pointer.
  - effective label pointer.
  - KLPD pointer.
  - SID pointer.
  - supplemental groups pointer.
  - dynamic audit info follows when audit is enabled.

## Macros

- `CR_PRIVS(c)`: address of credential privilege state.
- `CR_PRIVSETS(c)`: privilege set array.

## Important Notes

The file explicitly states:

- It is not public.
- Credentials are shared and read-only after finalization except for `cr_ref`.
- Kernel modules should use accessors in `cred.h`.
- Credential size depends on `ngroups_max`; callers cannot safely declare one directly.
- Correctly sized credentials come from allocation/copy routines.

## Research Relevance

Critical when tracing low-level credential lifetime, memory layout, privilege checks, and VFS authorization behavior.
