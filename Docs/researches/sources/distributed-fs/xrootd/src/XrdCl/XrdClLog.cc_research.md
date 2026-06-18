# sources/distributed-fs/xrootd/src/XrdCl/XrdClLog.cc

## Purpose

This file implements XrdCl diagnostic output sinks and message formatting. It turns severity/topic-gated log calls into timestamped lines written to stderr or a configured file.

## Important APIs, Types, And Functions

`LogOutFile::Open`, `Close`, and `Write` manage append-only file output. `LogOutCerr::Write` writes to `std::cerr` under `XrdSysMutex`. `Log::Say` formats printf-style messages, prefixes each line with local timestamp, severity, topic string, and optional PID, then delegates to the current output sink. `SetTopicName`, `LogLevelToString`, `StringToLogLevel`, `TopicToString`, and severity wrappers `Error`, `Warning`, `Info`, `Debug`, and `Dump` implement the public logging behavior.

## Control Flow

Each severity method first checks the current log level and topic mask. If enabled, it starts a `va_list` and calls `Say`. `Say` grows a temporary buffer until `vsnprintf` fits, splits multi-line messages with `XrdOucTokenizer`, formats metadata, and writes the final string once.

## State And Persistence

`LogOutFile` persists messages to a file descriptor opened with `O_WRONLY | O_APPEND | O_CREAT` and user read/write permissions. `Log` maintains topic names, maximum topic width, masks, output sink pointer, and optional PID. The file does not persist configuration itself; it only writes log lines.

## Dependencies And Integration Points

It uses POSIX file APIs, `XrdSysE2T` for errno text, `XrdOucTokenizer` for line splitting, `XrdClOptimizers.hh` branch hints, and `XrdClLog.hh` declarations. It is used throughout XrdCl through `DefaultEnv::GetLog()`.

## Risks

`Log::SetOutput` deletes the current sink without synchronization, so changing sinks while other threads log is unsafe. `LogOutFile::Write` does not retry partial writes. `pTopicMap.rbegin()` is used by `RegisterTopic` in the header and requires at least one topic to exist before dynamic registration. Formatting errors are reported through the log output but not otherwise surfaced.

## Test Signals

Good signals include severity filtering, topic mask filtering, file-open failure behavior, multi-line formatting, long-message buffer growth, concurrent stderr writes, optional PID formatting, string-to-level parsing, and partial/closed file descriptor error paths.
