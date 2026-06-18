<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/User/Scripts/scripts.ini.xml -->
# sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/User/Scripts/scripts.ini.xml

Purpose: XML-normalized user logon scripts policy fixture.

Important APIs/types/functions: root `IniFile`, section `Logon`, keys `0CmdLine` and `0Parameters`, and generalized `network_path` token for a netlogon batch file.

Control flow: static INI representation of one logon script command with empty parameters.

State and persistence behavior: fixture only.

Dependencies and integration points: exercises user script GPO backup/restore and UNC path generalization.

Risks: custom network path entity must be resolved by Samba tooling; empty parameter value is semantically significant.

Test signals: restored scripts.ini should contain the logon command and blank parameters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/User/Scripts/scripts.ini.xml -->
