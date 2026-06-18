<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/LoggerSource.java -->
# sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/LoggerSource.java

Purpose: descriptor for a remote logger to adjust and stream for an insight point.

Important APIs: stores `Component`, logger name string, and `Level`. Constructors accept an explicit logger name or a component type plus Java class, using `Class.getCanonicalName`. Getters expose fields. `Level` enum supports TRACE, DEBUG, INFO, WARN, ERROR.

Control flow and integration: insight implementations return `LoggerSource` lists. `LogSubcommand` uses them to call `/logLevel`, match streamed log lines by logger name substring, and group source components.

State and persistence: immutable in practice, fields are not final. The descriptor itself is local only; applying it changes remote logging state.

Risks and tests: substring matching can include lines for nested or similarly named loggers. Canonical class names are compile-time coupled to Ozone internals. No direct unit tests for constructors or levels.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/insight/src/main/java/org/apache/hadoop/ozone/insight/LoggerSource.java -->
