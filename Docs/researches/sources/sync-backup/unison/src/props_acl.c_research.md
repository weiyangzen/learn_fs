# sources/sync-backup/unison/src/props_acl.c

Purpose: platform-specific ACL synchronization stubs for Unison.

Important APIs: `unison_acl_from_text(path, acl)` sets/removes ACLs; `unison_acl_to_text(path)` returns deterministic ACL text, empty string for no/trivial ACL, or `"-1"` for unsupported paths/platforms.

Control flow: unsupported platforms no-op on set and return not-supported. Windows converts SDDL to a security descriptor, applies DACL/protection flags with `SetNamedSecurityInfoW`, and when reading removes inherited ACEs before serializing SDDL. Unix-like code supports Solaris, FreeBSD, NetBSD, and Darwin using native ACL APIs, choosing NFSv4/POSIX/extended ACL types, stripping ACLs on empty input, normalizing text output, and detecting trivial ACLs.

State/persistence: mutates filesystem ACL metadata. Windows ignores inherited ACEs because they cannot be restored independently. Unix removals may strip ACLs back to mode-derived/trivial state.

Dependencies/integration: Windows ACL/SDDL APIs, Solaris ACL APIs, BSD/Darwin `<sys/acl.h>`, pathconf ACL capability checks, OCaml Failure exceptions, and `props.ml` archive/property logic.

Risks: ACL text is intentionally platform-specific, limiting cross-platform ACL sync. Subject identity mapping is hard, especially Windows SIDs versus Unix users/groups. Raw native normalization differences can cause repeated sync diffs. Windows access denied often needs restore/admin privileges.

Test signals: same-platform ACL roundtrip tests, inherited-ACE stripping tests, empty/trivial ACL detection, unsupported path behavior, permission-denied reporting, and cross-filesystem capability checks.
