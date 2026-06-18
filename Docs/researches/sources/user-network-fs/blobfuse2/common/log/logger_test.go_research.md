# sources/user-network-fs/blobfuse2/common/log/logger_test.go
## sources/user-network-fs/blobfuse2/common/log/logger_test.go

Purpose: validates the logger factory/facade across base, silent, syslog, and invalid logger types.

Important APIs/helpers: `LoggerTestSuite`, `fastTestDebug`, `fastTestCrit`, `simpleTest`, and suite tests `TestBaseLogger`, `TestSilentLogger`, `TestSysLogger`, `TestNegative`.

Control flow: `simpleTest` cycles through debug/info/warning levels and emits all severity methods. `TestBaseLogger` configures file logging to `./logfile.txt`, runs simple logging, emits 100k debug lines then 100k critical lines to drive rotation, and calls `Destroy`. `TestSilentLogger` ensures no-op logging accepts calls. `TestSysLogger` requests syslog at debug level and accepts factory fallback if syslog is unavailable. `TestNegative` expects an invalid type error.

State and persistence: writes `./logfile.txt` and rotated logs but does not remove them. Mutates package-global `logObj` and `timeTracker`.

Dependencies/integration: syslog availability, filesystem write permissions, asynchronous base logger goroutine, and testify.

Risks: high-volume logging makes the test relatively expensive. Leftover log files can dirty working directories. Syslog behavior may differ across platforms, but factory fallback avoids failing when service is absent. No assertions inspect log contents or rotation file count.

Test signals: confirms factory selection and that the async logger can survive large message volume plus destruction without returning errors.
