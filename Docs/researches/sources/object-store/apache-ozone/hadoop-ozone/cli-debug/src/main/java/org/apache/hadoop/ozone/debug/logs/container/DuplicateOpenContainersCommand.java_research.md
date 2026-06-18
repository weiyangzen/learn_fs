# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/DuplicateOpenContainersCommand.java

Purpose: `DuplicateOpenContainersCommand` lists containers with duplicate OPEN state entries in the parsed log database.

Important APIs and types: It implements `Callable<Void>`, uses parent `ContainerLogController`, and delegates to `ContainerDatanodeDatabase.findDuplicateOpenContainer`.

Control flow: The command resolves the DB path, constructs the database helper, calls the duplicate-open query/analysis method, and returns.

State and persistence behavior: It reads the SQLite database only.

Dependencies and integration points: It depends on tables populated by `ContainerLogParser` and analysis SQL/helper logic in utility classes.

Risks: All validation and output behavior is delegated; missing/invalid DB paths surface through the parent or database helper.

Test signals: Output listing container IDs and counts for duplicate OPEN states.
