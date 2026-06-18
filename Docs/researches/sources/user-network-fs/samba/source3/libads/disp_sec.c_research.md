# sources/user-network-fs/samba/source3/libads/disp_sec.c

## Purpose
`disp_sec.c` prints Active Directory security descriptors, ACLs, ACEs, access masks, trustees, and object GUID annotations for diagnostic command output.

## Important APIs and Functions
Under `HAVE_LDAP`, `ads_disp_sd` is the public printer. Static helpers include `ads_disp_perms`, `ads_interprete_guid_from_object`, `ads_disp_sec_ace_object`, `ads_disp_ace`, and `ads_disp_acl`. The permission table maps selected AD/standard rights to text.

## Control Flow and State
`ads_disp_sd` lazily populates `ads->config.schema_path` and `ads->config.config_path` if possible, prints descriptor header/owner/group, then iterates SACL and DACL ACEs. Object ACE GUIDs are resolved first as schema attributes and then as extended rights. Output goes directly to stdout using `printf`.

## Dependencies and Integration Points
It depends on ADS schema/config lookup, GUID and SID formatting, security descriptor structures, and AD security right constants. It is integrated with tools such as `net ads` diagnostics rather than core server request paths.

## Risks and Test Signals
This is display code, but it mutates `ADS_STRUCT` config cache fields and assumes stdout is appropriate. The permission table contains duplicate `SEC_ADS_CONTROL_ACCESS` entries for change/reset password, so printed labels may be ambiguous. Tests should cover null descriptors, null ACLs, object ACEs with resolvable and unknown GUIDs, full-control masks, remaining unknown bits, and missing schema/config paths.
