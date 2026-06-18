# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/klpd.c

## Role

`klpd.c` implements kernel support for privilege-policy daemon upcalls. It lets userland door servers answer privilege policy questions for credentials, projects, zones, and `pfexec`.

## Registration Model

A `klpd_reg_t` stores a door handle, target pid, allowed privilege set, optional credential, disabled flag, reference count, and linked-list pointers.

Registrations can be:
- Credential-specific through `credklpd_t`.
- Project-specific through `kpj_klpd`.
- Global through `klpd_list`.
- Zone `pfexecd` specific through `zone_pfexecd`.

List nodes are refcounted and unlinked lazily so walkers can safely continue.

## KLPD Calls

`klpd_marshall()` builds a door-call payload containing the requested privilege set and optional argument data. Supported argument types include none, vnode path, integer, and protocol/port variants.

For vnode arguments it resolves a path relative to the registering credential’s zone root and optionally appends a caller-supplied component.

`klpd_call()` refuses to upcall while sensitive locks such as `pidlock`, `p_lock`, or `p_crlock` are held. It also enforces that the requested privilege set is within the caller’s limit set. It tries credential-specific registration first, then project registration, then global registrations visible to the caller’s zone.

`klpd_do_call()` prevents self-calls to the door server, retries `EAGAIN`, unregisters bad global doors on `EINVAL`/`EBADF`, validates the reply buffer, and treats malformed replies as denial.

## Register And Unregister

`klpd_reg()` validates the caller’s requested privilege set against its effective/outer effective privileges, validates the door, prevents same-process pid registrations from calling themselves, and registers by pid, project, or global scope.

For current-process pid registration it creates a new credential copy with a `credklpd_t` pointer. For another pid it requires an existing credential KLPD object and updates it in place.

`klpd_unreg()` removes project, pid, current-process, or global registrations depending on the supplied id type and id.

`crklpd_hold()`, `crklpd_rele()`, `crklpd_alloc()`, and `crklpd_setreg()` manage credential-attached registration state.

## Pfexec Support

`pfexec_reg()` and `pfexec_unreg()` manage a per-zone `pfexecd` door registration after privilege checks.

`pfexec_call()` asks `pfexecd` for execution attributes for a resolved path. A successful reply can allow execution unchanged or return a modified credential with uid/gid changes, inherited privileges, limit privileges, and scrub-environment requirements. Returned privilege sets must remain within the current limit set.

`get_forced_privs()` asks `pfexecd` for forced privileges for a path, intersects them with the zone kernel credential’s limit set, and rejects privileges outside the caller’s limit set.

`check_user_privs()` asks `pfexecd` whether a user is authorized for a requested privilege set.

## Research Notes

This file is a high-value security boundary. Important audit areas are door upcall error handling, avoiding userland callbacks with kernel locks held, refcount/list unlink rules, zone visibility, path construction and bounds, reply size/alignment validation, credential mutation from `pfexecd` replies, and strict enforcement that granted privileges never exceed limit privileges.
