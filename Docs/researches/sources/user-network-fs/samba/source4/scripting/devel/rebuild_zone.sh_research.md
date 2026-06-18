<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/rebuild_zone.sh -->
# sources/user-network-fs/samba/source4/scripting/devel/rebuild_zone.sh

Purpose: rebuilds a BIND zone file for a Samba AD domain by extracting DC GUIDs and generating common AD service records.

Important APIs/types/functions: `dcname`, `getip`, `ldbsearch`, `nmblookup`, here-doc zone template, and `rndc reload`.

Control flow: requires `sam.ldb` and output zone path, reads DNS hostname, realm, NTDS DSA objectGUIDs, and domain GUID, writes SOA/NS header, appends A records for each DC, emits `_msdcs`, LDAP, GC, Kerberos, and kpasswd SRV/CNAME/A records per DC, writes a Kerberos TXT record, and reloads BIND.

State and persistence behavior: overwrites the target zone file and reloads BIND. It reads sam.ldb but does not modify it.

Dependencies and integration points: intended for old BIND flat-file DNS setups. Depends on build-tree `ldbsearch`, NetBIOS name lookup, and system `rndc`.

Risks: IP discovery falls back to `XX.XX.XX.XX`, requiring manual edits. Site name is hardcoded to `Default-First-Site-Name`. Shell variables and output path are not robustly quoted.

Test signals: generated zone file contents, successful `rndc reload`, and DNS query results for generated records.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/rebuild_zone.sh -->
