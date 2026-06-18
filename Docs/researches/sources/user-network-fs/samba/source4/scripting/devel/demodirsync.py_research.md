<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/demodirsync.py -->
# sources/user-network-fs/samba/source4/scripting/devel/demodirsync.py

Purpose: demonstration and diagnostic client for LDAP DirSync controls and cookies against a Samba/AD LDAP server.

Important APIs/types/functions: `printdirsync`, `Ldb("ldap://host:389")`, `searchex`, `drsblobs.ldapControlDirSyncCookie`, `ndr_pack`, `ndr_unpack`, `base64`, and `misc.GUID`.

Control flow: requires `--host`, opens remote LDAP, performs an initial DirSync search to discover server invocation GUID, then performs multiple searches with no cookie, saved cookie, modified GUIDs, and modified high-watermarks. It prints continuation status, GUID, highest USN fields, extra cursor USN, and entry counts.

State and persistence behavior: read-only LDAP queries. Cookie objects are mutated in memory to exercise edge cases.

Dependencies and integration points: integrates LDAP DirSync control parsing with DRS blob structures and Samba LDB remote connections.

Risks: Python 2 shebang style and byte/string assumptions can be fragile on modern Python. It is a demo script, not a stable test harness, and intentionally tampers with cookies.

Test signals: printed cookie high-watermark transitions and returned entry counts indicate server DirSync behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/demodirsync.py -->
