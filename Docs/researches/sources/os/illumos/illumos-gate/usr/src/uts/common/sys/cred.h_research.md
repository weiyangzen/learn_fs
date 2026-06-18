# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cred.h

## Role

Defines the opaque credential type and kernel accessor/manipulation API.

## Main Type

- `typedef struct cred cred_t;`

The implementation is private in `sys/cred_impl.h`.

## Kernel Macros and Globals

- `CRED()`: current thread credential.
- `ngroups_max`: supplemental group limit.
- `kcred`: all-privileges kernel credential.

## Credential Lifecycle

- `cred_init()`
- `crhold()`, `crfree()`
- `cralloc()`, `cralloc_ksid()`
- `crget()`
- `crcopy()`, `crcopy_to()`
- `crdup()`, `crdup_to()`
- `crgetcred()`
- `crset()`
- `zone_kcred()`

## Identity and Permission APIs

- Group checks:
  - `groupmember()`
  - `supgroupmember()`
- Process permission checks:
  - `hasprocperm()`
  - `prochasprocperm()`
- Credential comparison:
  - `crcmp()`
- Accessors:
  - UIDs/GIDs: effective, real, saved.
  - zone id and project id.
  - audit info and modifiable audit info.
  - refcount.
  - group list and group count.
  - mapped credential.

## Mutation APIs

- UID/GID setting:
  - `crsetresuid()`
  - `crsetresgid()`
  - `crsetugid()`
- Supplemental groups:
  - `crsetgroups()`
  - `crgrpcopyin()`
  - `crgrprele()`
  - `crsetcredgrp()`
- Zone/project:
  - `crsetzone()`, `crgetzone()`
  - `crsetprojid()`
- NFS:
  - `crnetadjust()`
- procfs:
  - `cred2prcred()`
- Trusted Solaris/Rampart:
  - `crgetlabel()`
  - `crisremote()`
- Ephemeral IDs:
  - `VALID_UID()`, `VALID_GID()`
  - `valid_ephemeral_uid()`, `valid_ephemeral_gid()`
  - `eph_uid_alloc()`, `eph_gid_alloc()`
- SIDs and privileges:
  - `crsetsid()`, `crsetsidlist()`
  - `crgetsid()`, `crgetsidlist()`
  - `crsetpriv()`
- KLPD:
  - `crgetcrklpd()`
  - `crsetcrklpd()`

## Research Relevance

Credentials are central to VFS permission checks, zones, projects, NFS identity handling, auditing, and privilege enforcement.
