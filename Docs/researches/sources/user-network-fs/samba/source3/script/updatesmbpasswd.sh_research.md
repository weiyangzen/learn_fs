# sources/user-network-fs/samba/source3/script/updatesmbpasswd.sh

Purpose: filter script for updating or sanitizing smbpasswd-style colon-separated records, preserving comments and replacing invalid password hashes with `XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`.

Important functions and APIs: implemented as a `nawk` program with `FS=":"`. It checks whether a line begins with `#`, whether field 4 is a 32-character all-hex, all-`X`, or all-`*` hash, and otherwise reconstructs the line with fields 1-3 preserved and field 4 replaced.

Control flow: for each input line, comments are printed unchanged; valid hash lines are printed unchanged; invalid hash lines are rewritten as `user:uid:...:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX:` followed by fields 4 through `NF` and a trailing colon.

State and persistence: stateless stream filter. It reads stdin and writes stdout, leaving file replacement to callers.

Dependencies and integration: uses `nawk` and smbpasswd file format assumptions. It is an administrative compatibility script rather than a selftest.

Risks and test signals: the reconstruction loop starts at original field 4 after already outputting a replacement hash, so it appends the invalid original field as subsequent data; this may be intentional for legacy field shifting or may duplicate data unexpectedly. It also only accepts uppercase hex. Correct behavior should be checked with representative smbpasswd lines.
