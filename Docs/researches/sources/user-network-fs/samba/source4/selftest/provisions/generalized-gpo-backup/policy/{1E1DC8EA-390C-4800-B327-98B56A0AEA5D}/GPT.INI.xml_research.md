<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/GPT.INI.xml -->
# sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/GPT.INI.xml

Purpose: XML-normalized Group Policy Template INI fixture for a generalized GPO backup.

Important APIs/types/functions: root `IniFile`, section `General`, parameters `Version=1179715` and `displayName=New Group Policy Object`.

Control flow: static data maps original `GPT.INI` content into Samba's XML backup representation.

State and persistence behavior: fixture only; no mutation.

Dependencies and integration points: consumed by GPO backup/restore tests that split generalized XML from concrete `.SAMBABACKUP` files.

Risks: policy version must remain synchronized with the paired backup file. XML structure is simple but order-sensitive tests may rely on parameter order.

Test signals: parser should reconstruct the General section and exact version/display name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/GPT.INI.xml -->
