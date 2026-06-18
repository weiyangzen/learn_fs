<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/LogSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/LogSubcommand.java

Purpose: picocli `log`/`logs` subcommand that temporarily raises related remote loggers and streams matching log events from Ozone HTTP logstream endpoints.

Important APIs: parameters `insightName`, options `-v` and `-f`. `call()` resolves the insight, obtains `LoggerSource` descriptors, sets requested log levels, registers a shutdown hook restoring them to INFO, de-duplicates source components, and streams logs. `streamLog` starts one thread per component and joins them. Per-component `streamLog` opens `<host>/logstream`, filters lines by logger name plus insight filter, formats embedded `<json>...</json>` payloads through `processLogLine`, prefixes output with `[component-prefix]`, and prints. `setLogLevel` calls `<host>/logLevel?log=name&level=level` and requires HTTP 200.

Control flow and integration: depends on `InsightHttpUtils` for authenticated HTTP, `BaseInsightSubCommand.getHost` for endpoint resolution, and Ozone HTTP log endpoints supporting `/logLevel` and `/logstream`. The command is long-running because it joins streaming threads.

State and persistence: remotely mutates logger levels until process shutdown or explicit shutdown hook execution. No local persistence.

Risks and tests: if the process is killed abruptly, remote log levels may stay elevated. Query parameters are not URL-encoded, so logger names or levels with special characters would be risky; current enum/logger values are controlled. `streamLog` can run indefinitely and propagates IO failures as runtime exceptions from worker threads. `processLogLine` uses greedy regex matching across a line and replaces escaped newlines. `TestLogSubcommand` covers JSON newline expansion only, not HTTP, threading, or level restoration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/LogSubcommand.java -->
