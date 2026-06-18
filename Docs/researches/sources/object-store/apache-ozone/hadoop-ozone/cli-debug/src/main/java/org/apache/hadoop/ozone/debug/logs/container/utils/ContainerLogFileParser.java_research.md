# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/logs/container/utils/ContainerLogFileParser.java

Purpose: `ContainerLogFileParser` scans extracted container log files, parses structured log lines into `DatanodeContainerInfo`, and persists parsed records through `ContainerDatanodeDatabase`.

Important APIs and types: The public API is `processLogEntries(String, ContainerDatanodeDatabase, int)`. Internally it uses `Files.walk`, a fixed thread pool, `CountDownLatch`, an `AtomicBoolean` failure flag, and a private `processFile` parser. It recognizes `ID`, `BCSID`, `State`, and `Index` key-value fields split by `" | "`.

Control flow: The directory walk collects regular files, derives the datanode ID from the substring after `.log.`, and submits each valid file to the executor. `processFile` reads lines as UTF-8, extracts timestamp and log level from the first two fields, parses key-value fields, treats non-key fields as an error/message string, filters to `Index=0`, batches up to 5000 entries, and inserts each batch.

State and persistence behavior: The parser itself stores only the `hasErrorOccurred` flag and per-file batch lists. Durable state is delegated to SQLite through `insertContainerDatanodeData`. Invalid filenames are skipped with console messages; malformed lines without an ID are logged but do not abort.

Dependencies and integration points: It integrates with the database utility and expects log naming in the form containing `.log.<datanodeId>`. It is part of the container log debug pipeline that first creates tables, then parses files, then derives latest-state rows.

Risks: `line.split` assumes every line has timestamp and log-level fields; short or malformed lines can throw unchecked exceptions and mark the worker failed. Latch count is initialized to all regular files, including skipped invalid names, but skipped files do not count down, so invalid filenames can deadlock. The thread pool is shut down only after latch wait. The index filter currently excludes EC/non-zero replica index data.

Test signals: Tests should include multiple files, invalid filenames, empty datanode IDs, malformed lines, non-zero index filtering, batch flush at and below 5000, propagated SQL failure, and no hang when files are skipped.
