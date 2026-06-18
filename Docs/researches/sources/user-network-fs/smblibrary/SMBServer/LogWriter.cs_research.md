<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/LogWriter.cs -->
# sources/user-network-fs/smblibrary/SMBServer/LogWriter.cs

## Purpose
Sample server log sink that writes `LogEntry` events to daily log files under a `Logs` directory beside the executable.

## APIs, Types, and Functions
Constructors choose default or explicit log directory. Methods include `OpenLogFile()`, `CloseLogFile()`, `WriteLine()` overloads, `OnLogEntryAdded()`, and `GetAssemblyDirectory()`.

## Control Flow, State, and Persistence
Writes are protected by `m_syncLock`. `OpenLogFile()` rotates when the date changes, creates the logs directory if needed, and opens the daily file in append/write-through mode. Exceptions while opening are swallowed, disabling logging. `OnLogEntryAdded()` filters out `Trace` severity and formats one line per event. Persistent state is daily log files.

## Dependencies and Integration
Used by `ServerUI` as a synchronous subscriber to `SMBServer.LogEntryAdded`.

## Risks and Test Signals
Risks include swallowed open errors, no disposal interface, creating a new `StreamWriter` per line, synchronous disk I/O on server activity, and Windows path separators. Test log directory creation, date rotation, concurrent log events, permission failures, and close/reopen behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/LogWriter.cs -->
