<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Microsoft/Windows NT/SecEdit/GptTmpl.inf.xml -->
# sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Microsoft/Windows NT/SecEdit/GptTmpl.inf.xml

Purpose: XML-normalized security template fixture for machine policy settings.

Important APIs/types/functions: root `GptTmplInfFile`; sections for Unicode, Version, System Access, Kerberos Policy, logs, Event Audit, Registry Values, Privilege Rights, Service General Setting, Registry Keys, File Security, and Group Membership. It includes password history, guest enablement, Kerberos max renew age, event audit, registry values, privilege user tokens, ACL token placeholders, and group membership tokens.

Control flow: static section/parameter representation of a UTF-16 `GptTmpl.inf` policy backup.

State and persistence behavior: fixture only.

Dependencies and integration points: exercises Samba GPO backup restore logic for security templates, SID/user ID generalization, registry ACLs, service settings, and group membership.

Risks: custom entity tokens and empty values require specialized XML handling. Sections with no parameters are still meaningful and must not be dropped.

Test signals: restore should recreate the original secedit template, including user/ACL substitutions and empty sections.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Microsoft/Windows NT/SecEdit/GptTmpl.inf.xml -->
