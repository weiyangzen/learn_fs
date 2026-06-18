# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cred.c

## Role

`cred.c` implements illumos kernel credential management. It owns allocation, reference counting, copying, mutation, user/group membership checks, process permission checks, privilege manipulation, audit-label export, zone-aware credentials, kernel credential setup, and ephemeral ID/SID support.

This file is security-sensitive: credentials flow into process identity, vnode permission checks, privilege policy, auditing, labeled security, remote peer identity, NFS behavior, and zone isolation.

## Initialization

`cred_init()` initializes privilege infrastructure, determines whether C2 audit support is loaded, sizes the credential allocation including optional audit storage, creates `cred_cache`, initializes `dummycr`, and creates `kcred`.

`kcred` is the all-powerful kernel credential template. It is associated with `zone0`, has a full limit set, basic inheritable/effective/permitted sets, adjustments for `rstchown` and `rstlink`, and `NET_MAC_AWARE`.

The function also assigns `kcred` to process 0 and the current thread, initializes `ucredsize`, and creates zone-specific storage for ephemeral identity state.

## Allocation and Reference Management

Core allocation and lifecycle functions include:

- `cralloc_flags()` and `cralloc()`: allocate nearly uninitialized credentials.
- `cralloc_ksid()`: allocate with SID storage when ephemeral IDs have been used.
- `crget()`: allocate an initialized credential from the current zone’s kernel credential.
- `crhold()`: increment `cr_ref`.
- `crfree()`: decrement `cr_ref` and release labels, klpd, zone holds, SID data, group data, and cache storage when it reaches zero.
- `crcopy()` and `crcopy_to()`: copy and replace a credential, dropping the old reference and returning a two-reference credential for process/thread use.
- `crdup()`, `crdup_flags()`, and `crdup_to()`: duplicate credentials without freeing the source.

Shared subobjects are held or released explicitly: zones, labels, SID records, kernel privilege daemons, and supplemental groups.

## Process and Thread Credential Updates

`crset()` broadcasts a new credential to a process. It directly updates the current thread’s `t_cred` and marks other LWPs in the same process with `t_pre_sys` so they adopt the process credential at their next syscall/trap boundary. This avoids changing another thread’s credential in the middle of a system call.

`crgetcred()` returns a held copy of the current process credential under `p_crlock`.

## Group and Permission Checks

`groupmember()` checks effective group first and then supplemental groups. `supgroupmember()` uses linear search for small group lists and binary search for larger sorted lists.

`hasprocperm()` implements process-credential permission checks for signal-like operations:

- same credential succeeds,
- cross-zone access requires global-zone/zone privilege,
- matching real/effective/saved user IDs succeeds,
- `PRIV_PROC_OWNER` succeeds.

`prochasprocperm()` is the preferred wrapper when process pointers are available. It succeeds for the same process, enforces session/basic process policy, safely obtains the target credential, and calls `hasprocperm()`.

`crcmp()` compares credentials for same-user equivalence, including IDs, zone, supplemental groups, and effective/permitted privilege equivalence.

`suser()` is the compatibility superuser check using `PRIV_SYS_SUSER_COMPAT`.

## Accessors and Mutators

The file provides many simple accessors:

- UID/GID: `crgetuid()`, `crgetruid()`, `crgetsuid()`, `crgetgid()`, `crgetrgid()`, `crgetsgid()`.
- Audit: `crgetauinfo()`, `crgetauinfo_modifiable()`.
- Zone/project: `crgetzoneid()`, `crgetprojid()`, `crgetzone()`.
- Label: `crgetlabel()`.
- Remote marker: `crisremote()`.
- Groups: `crgetgroups()`, `crgetngroups()`.
- Refcount: `crgetref()`.

Mutation helpers include:

- `crsetresuid()`
- `crsetresgid()`
- `crsetugid()`
- `crsetgroups()`
- `crsetprojid()`
- `crsetzone()`

Mutators assert the credential has at most the expected mutable references and validate IDs against the credential’s zone.

Supplemental groups are stored in `credgrp_t`, sorted on set/copyin, reference-counted with `crgrphold()` and `crgrprele()`, and can be installed with `crsetcredgrp()`.

## User Credential Export

`cred2prcred()` converts kernel credentials into `/proc` `prcred_t`.

`cred2ucaud()` exports audit information if the receiver has audit-getattr policy rights.

`cred2uclabel()` copies the credential label.

`cred2ucred()` builds a user-visible `ucred_s`:

- Records size, PID, project ID, and zone ID.
- For remote peer credentials, exports only the label when available.
- For normal credentials, includes `prcred`, privilege data, optional audit data, and optional label data.
- Supports caller-provided aligned buffers.

`ucredminsize()` computes the minimal required allocation, avoiding unused supplemental group slots and handling remote/labeled credentials.

`pgetucred()` obtains a held process credential and exports it as a `ucred_s`.

## Audit and Label Support

Audit storage is conditionally embedded after `cred_t` depending on `get_c2audit_load()`, which checks whether `c2audit` is excluded.

Trusted Extensions label helpers include:

- `newcred_from_bslabel()`
- `copycred_from_tslabel()`
- `copycred_from_bslabel()`

`crgetlabel()` returns a credential label when present or falls back to the zone label.

## Zone Kernel Credentials

`zone_kcred()` returns the kernel credential equivalent for the current zone when available, otherwise global `kcred`.

`crsetzone()` updates a credential’s zone pointer by holding the new zone before releasing the old zone, which is safe when old and new are identical.

## NFS Credential Adjustment

`crnetadjust()` supports an NFS retry case: if the effective UID is root but the real UID is non-root, it duplicates the credential and changes effective UID to the real UID so network access can be retried without root identity.

## Ephemeral IDs and SID Mapping

The file maintains per-zone ephemeral identity state in `ephemeral_zsd_t`, created lazily by `get_ephemeral_zsd()` and freed through the zone-specific-data destructor.

Per-zone state tracks:

- minimum and last ephemeral UID
- minimum and last ephemeral GID
- lock
- an `eph_nobody` credential used when SID-containing credentials must map to nobody

Functions include:

- `valid_ephemeral_uid()`
- `valid_ephemeral_gid()`
- `eph_uid_alloc()`
- `eph_gid_alloc()`
- `get_ephemeral_data()`
- `set_ephemeral_data()`

Allocation detects unsigned wraparound, supports state reset/corruption flags, sets global `hasephids`, and returns ranges.

`crgetmapped()` maps credentials with user or group SIDs above `MAXUID` to the zone’s `eph_nobody` credential. It also tolerates `NULL` credentials passed incorrectly to vnode operations.

SID manipulation APIs include:

- `crsetsid()`
- `crsetsidlist()`
- `crgetsid()`
- `crgetsidlist()`

## Privilege and KLPD Helpers

`crsetpriv()` is a kernel-server helper that resets privilege sets and adds named privileges to permitted/effective sets without performing security checks.

`crset_zone_privall()` expands a credential to all privileges allowed by its zone privilege set.

`crgetcrklpd()` and `crsetcrklpd()` get and set the credential’s kernel privilege daemon state with reference release on replacement.

## Research Notes

This file is central to illumos security semantics. The most important invariants are credential immutability while shared, correct reference handling for all embedded objects, zone-aware ID validation, sorted supplemental groups for binary search, safe process/thread credential replacement timing, and careful separation between local, remote-peer, labeled, audited, and SID-bearing credentials.
