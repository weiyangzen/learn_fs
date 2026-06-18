<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/User/Documents & Settings/fdeploy1.ini.xml -->
# sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/User/Documents & Settings/fdeploy1.ini.xml

Purpose: XML-normalized folder redirection fixture with two redirected folders.

Important APIs/types/functions: root `IniFile`, `version` section, `Folder_Redirection` section mapping folder GUIDs to generalized user IDs, per-folder sections keyed by `fdeploy_GUID` and `fdeploy_SID`, flags `1219`/`1211`, and generalized network paths for Pictures and Desktop.

Control flow: static folder-redirection INI representation with tokenized SIDs and UNC paths.

State and persistence behavior: fixture only.

Dependencies and integration points: exercises GPO backup/restore handling for folder redirection, user SID abstraction, network path abstraction, and directories with spaces.

Risks: XML entity tokens require custom handling. GUID section attributes and parameter keys both carry semantic identity and must be preserved.

Test signals: restore should recreate folder redirection settings for the two GUIDs and network paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/User/Documents & Settings/fdeploy1.ini.xml -->
