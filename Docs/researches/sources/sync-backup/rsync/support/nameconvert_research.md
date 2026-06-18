<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/nameconvert -->
# sources/sync-backup/rsync/support/nameconvert

Purpose: stdin/stdout daemon helper protocol for converting user and group IDs to names and names to IDs.

Important APIs/types/functions: `main()` reads requests and uses Python `pwd` and `grp` modules. Supported request prefixes are `uid`, `gid`, `usr`, and `grp`.

Control flow: for each input line, split into request and argument, dispatch to `pwd.getpwuid`, `grp.getgrgid`, `pwd.getpwnam`, or `grp.getgrnam`, print an empty line for unknown names/IDs, and exit with an error on malformed or unsupported requests.

State and persistence behavior: stateless stream processor; no filesystem mutation.

Dependencies and integration points: depends on Python 3 and local NSS/passwd/group resolution. Used by rsync daemon configurations via the `name converter` setting, often when chrooting changes visibility of system account databases.

Risks: lookups can block or vary depending on NSS backends. Malformed input terminates the process, which is appropriate for protocol errors but can break a daemon session. It trusts local system account data.

Test signals: feed each valid request type, unknown users/groups, malformed request lines, and verify flushing per response for daemon interaction.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/nameconvert -->
