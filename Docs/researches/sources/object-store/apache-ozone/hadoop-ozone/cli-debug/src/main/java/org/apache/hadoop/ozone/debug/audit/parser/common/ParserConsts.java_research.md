# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/audit/parser/common/ParserConsts.java

Purpose: `ParserConsts` centralizes constants for the audit parser SQLite and log parsing implementation.

Important APIs and types: It defines JDBC driver `org.sqlite.JDBC`, SQLite connection prefix, audit date regex, properties resource name, and SQL property keys.

Control flow: There is no dynamic flow besides class loading.

State and persistence behavior: Constants guide persistent SQLite connection creation and table SQL lookup; the class itself has no state.

Dependencies and integration points: `DatabaseHelper` uses all constants to load resources, detect new audit entries, and open SQLite connections.

Risks: `DATE_REGEX` accepts any line beginning with `yyyy-MM-dd`, so log formats that begin that way but are not audit entries could be misclassified.

Test signals: Correct constants are indirectly validated by audit parser load/query behavior.
