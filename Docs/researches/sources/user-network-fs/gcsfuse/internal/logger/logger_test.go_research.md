## sources/user-network-fs/gcsfuse/internal/logger/logger_test.go

### Purpose
`logger_test.go` is the behavioral test suite for logger formatting, severity filtering, log-file configuration, mount UUID generation, and severity-to-function lookup.

### Important APIs, Types, And Functions
Helpers include `expectedLogRegex`, `redirectLogsToGivenBuffer`, `getTestLoggingFunctions`, `fetchAllLogLevelOutputsForSpecifiedSeverityLevel`, and `validateLogOutputs`. Tests cover text and JSON output at `OFF`, `ERROR`, `WARNING`, `INFO`, `DEBUG`, and `TRACE`; `setLoggingLevel`; `InitLogFile`; `UpdateDefaultLogger`; UUID generation/setup; and `GetLogFHandler`.

### Control Flow
Most format tests set `defaultLoggerFactory.format`, redirect output to a buffer with a prefix and mount-id attr, run each logging helper, and compare captured lines against regexes. UUID tests reset package globals with `t.Cleanup` and use environment variables for background mode. `GetLogFHandler` tests direct handlers and the fallback path for unsupported levels, expecting both a warning and a trace log.

### State, Persistence, And Dependencies
Tests mutate logger globals, `programLevel`, environment variables, and temp log files. They depend on `testify`, regex matching, and default config constants.

### Integration Points
The tests protect the log schema consumed by log collectors: text severity key, JSON timestamp object, `message` key, and `mount-id`. They also check the per-mount identity behavior used by metrics and operational debugging.

### Risks
Because global logger state is shared, tests must isolate state carefully; some subtests reset factory fields but not every global. Regexes assume timestamp lengths and mount UUID format. Syslog and rotation are not covered.

### Test Signals
Signals are comprehensive for level filtering and formatting of the main logging helpers. Additional value would come from testing `NewLegacyLogger`, syslog fallback, invalid severity strings, and file rotation.
