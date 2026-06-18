# sources/user-network-fs/cifs-utils/setcifsacl.rst.in

## Purpose
This reStructuredText input is the manual page for `setcifsacl(1)`. It documents the command-line contract for modifying CIFS/NTFS security descriptor ACLs, SACLs, owner SIDs, and group SIDs on CIFS-mounted file objects.

## Important APIs and options
The documented interface exposes `-h`, `-v`, `-U`, `-a`, `-A`, `-D`, `-M`, `-S`, `-o`, and `-g`. ACE entries are documented as `ACL:SID:TYPE/FLAGS/MASK`, with multiple entries comma-separated inside quotes. DACL types include `ALLOWED`, `DENIED`, `OBJECT_ALLOWED`, and `OBJECT_DENIED`; SACL types include audit/object/callback/resource labels. Masks support symbolic `FULL`, `CHANGE`, `READ`, combinations of `R W X D P O`, or numeric hex values. Owner/group SIDs may be names or raw SID strings, relying on the configured idmap plugin.

## Control flow described
The manual describes one-shot transformations: add, add with preferred ordering, delete exact ACEs, modify ACEs matched by SID and type, replace an ACL, set owner SID, or set group SID. `-U` retargets ACE operations from DACL to SACL and is not meaningful for owner/group changes.

## State and persistence behavior
The documented state is the CIFS server-side security descriptor obtained and written through the Linux CIFS client. The manpage makes clear that server behavior decides whether the descriptor is actually applied and that kernel support is required.

## Dependencies and integration points
The template contains `@pluginpath@`, so build configuration injects the idmap plugin location. It cross-references `mount.cifs(8)` and `getcifsacl(1)` and should stay synchronized with `setcifsacl.c` parser behavior and cifs-utils install paths.

## Risks
There are documentation-code mismatches: the manpage uses `OBJECT_ALLOWED`/`OBJECT_DENIED`, while the C parser accepts `ALLOWED_OBJECT`/`DENIED_OBJECT`; DACL flag text mentions `NI`/`IA`, while code accepts `NP`/`I`; and SACL `MANDATORY_LABEL` is documented but the C parser contains a misspelled string. These mismatches can produce user-facing failures even when implementation logic works.

## Test signals
Run generated manpage builds, check examples against the compiled binary parser, and include documentation linting for option spellings and macro substitution. Integration tests should verify each example either succeeds or is intentionally corrected.
