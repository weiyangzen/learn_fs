# sources/user-network-fs/samba/source3/libgpo/gpext/security.c

## Purpose

Registers a skeletal Group Policy Security extension. It opens cached `Microsoft/Windows NT/SecEdit/GptTmpl.inf` files, validates their security-template headers, and leaves actual template application as a no-op placeholder.

## Important APIs, Types, and Functions

`gpext_security_init` registers `security_methods` for `GP_EXT_GUID_SECURITY`. `gpttmpl_parse_header` validates `[Version] signature="$CHICAGO$"`, `Revision`, and `[Unicode] Unicode=true`. `gpttmpl_init_context` opens the INI file and validates the header. `gpttmpl_process` currently returns success without applying sections. `security_process_group_policy` drives GPO iteration. `security_get_reg_config` advertises `ProcessGroupPolicy`, `NoUserPolicy`, and `ExtensionDebugLevel`.

## Control Flow

The process callback ignores deleted GPOs, iterates changed GPOs, resolves cache paths, opens `GptTmpl.inf`, validates the header, calls the no-op processing hook, and frees the INI context. Any resolution or validation failure aborts the loop and logs the NTSTATUS.

## State and Persistence Behavior

Only static registration context is kept. The current implementation reads cached template files but does not persist policy settings because `gpttmpl_process` is empty.

## Dependencies and Integration Points

Depends on libgpo INI helpers and the GPO extension ABI. Constants name expected security template sections including Registry Values, System Access, Kerberos Policy, Event Audit, Privilege Rights, group membership, file security, and service settings. Built as `gpext_security`.

## Risks and Test Signals

Primary risk is incomplete behavior: valid templates are accepted but not applied. Deleted-GPO cleanup is also absent. Tests should cover registration, strict header validation, cache path failures, and the current no-op behavior as an explicit expected signal.
