<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/watch_servers.sh -->
# sources/user-network-fs/samba/source4/scripting/devel/watch_servers.sh

Purpose: repeatedly compares LDAP search output from two servers.

Important APIs/types/functions: `watch`, `ldbsearch -S`, administrator credentials, filter pattern, and optional attributes.

Control flow: requires two DB/server URLs, password, search expression, and optional attrs; runs `watch -n1` with two `ldbsearch` commands, filtering boilerplate lines and deduplicating output with `uniq`.

State and persistence behavior: read-only polling.

Dependencies and integration points: developer replication/debug helper for comparing two Samba/AD servers.

Risks: password appears in the watch command line. Shell quoting is brittle for complex LDAP filters or attributes.

Test signals: live side-by-side terminal output showing differences or convergence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/watch_servers.sh -->
