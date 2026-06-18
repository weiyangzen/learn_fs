<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/GetScmRatisRolesSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/GetScmRatisRolesSubcommand.java

Purpose: Lists SCM Ratis roles and peer identity data in raw, table, or JSON form.

Important APIs and types: `ScmClient.getScmRoles()`, `JsonUtils`, `FormattingCLIUtils`, Picocli `--json`/`--table`, and role strings split by colon.

Control flow: `execute()` gets role strings. JSON mode parses each string into a map keyed by hostname with address, optional raft role, ID, and InetAddress. Table mode splits each role string and adds it to a five-column table. Default mode prints raw role strings. Invalid split results print an error to stderr; JSON returns an empty map for invalid input.

State and persistence behavior: Read-only. It formats SCM-reported role strings and stores no state.

Dependencies and integration points: Registered as `ozone admin scm roles`; depends on SCM Ratis role string format.

Risks: The parser assumes colon-separated fields and may mishandle IPv6-style addresses. Table mode warns but still attempts to add invalid rows. `--json` takes precedence over `--table`.

Test signals: Valid five-field roles, two-field no-Ratis roles, invalid responses, JSON/table/default output, and option precedence.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/scm/GetScmRatisRolesSubcommand.java -->
