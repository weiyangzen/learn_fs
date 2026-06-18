<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Scripts/scripts.ini.xml -->
# sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Scripts/scripts.ini.xml

Purpose: XML-normalized machine startup/shutdown scripts policy fixture.

Important APIs/types/functions: root `IniFile`, sections `Shutdown` and `Startup`, parameters `0CmdLine` and `0Parameters`, and generalized `network_path` entity placeholders.

Control flow: static INI representation for machine scripts, mapping commands to network paths and blank parameter values.

State and persistence behavior: fixture only.

Dependencies and integration points: tests GPO script policy backup/restore and network path generalization.

Risks: custom network path entities need Samba-specific substitution. Blank parameter values must be preserved.

Test signals: restore should recreate startup/shutdown script INI entries with substituted UNC paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Scripts/scripts.ini.xml -->
