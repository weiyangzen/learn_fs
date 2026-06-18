# sources/security-integrity/selinux/libsepol/src/write.c

## Purpose
`write.c` serializes an in-memory `policydb_t` into binary kernel, base, and module policy formats. It is the persistence counterpart to policydb read logic and is heavily version- and platform-gated.

## Important APIs and Control Flow
The exported entrypoint is `policydb_write()`. Helpers serialize ebitmaps, avtabs, MLS levels/ranges, symbol datums, constraints, conditionals, contexts, object contexts, genfs entries, range transitions, module avrules, scope indices, declarations, and blocks. `policydb_write()` writes magic/string/version/config counts, optional module name/version, policycaps, kernel permissive/neveraudit maps, symbol tables, then kernel-specific or module/base-specific rule structures, followed by ocontexts, genfs, range transitions, and type-attribute maps.

## State and Persistence
All output flows through `put_entry()`. Scalars are little-endian encoded. The writer may omit or warn about unsupported fields when targeting older policy versions: role/type attributes, non-process transitions, conditionals, permissive/neveraudit maps, GLBLUB defaults, filename transitions, and xperms.

## Dependencies and Integration
It depends on `private.h`, ebitmap, avtab, conditionals, expand helpers for old avtab formats, MLS serialization, policy compatibility lookup, and diagnostics. Its layout must remain aligned with read-side code and `policydb_validate.c`.

## Risks and Test Signals
Downgrade paths intentionally lose semantics with warnings. Old avtab writing expands attributes and uses `merged` flags. Xperms are rejected for old versions, unsupported conditional formats, and non-SELinux targets. Tests should include write/read round trips, downgrade warnings, xperm rejection, SELinux/Xen ocontext layouts, filename transition formats, MLS user formats, and `PF_LEN` length matching actual output.
