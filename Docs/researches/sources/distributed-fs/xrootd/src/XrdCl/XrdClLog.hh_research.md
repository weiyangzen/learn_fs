# sources/distributed-fs/xrootd/src/XrdCl/XrdClLog.hh

## Purpose

This header defines the XrdCl logging interface, output sink abstraction, severity levels, topic masking, and topic-name registry used across the client library.

## Important APIs, Types, And Functions

`LogOut` is the sink interface. `LogOutFile` writes to a file descriptor and `LogOutCerr` writes to stderr. `Log` exposes `Error`, `Warning`, `Info`, `Debug`, `Dump`, `Say`, `SetLevel`, `SetOutput`, `SetMask`, `SetTopicName`, `RegisterTopic`, `GetLevel`, and `SetPid`. `LogLevel` defines `NoMsg`, `ErrorMsg`, `WarningMsg`, `InfoMsg`, `DebugMsg`, and `DumpMsg`.

## Control Flow

Callers invoke a severity method with a topic bit and printf-style format. The implementation checks atomic `pLevel`, applies the mask for that severity, then formats in `Say`. Topic registration left-shifts the current highest topic number and stores a padded display name.

## State And Persistence

`Log` stores an atomic log level, masks indexed by severity, a heap-owned output sink, topic map, topic width, and PID. `LogOutFile` stores an open file descriptor. Persistence is limited to the sink chosen by the embedding environment.

## Dependencies And Integration Points

The header uses `<atomic>`, `<map>`, `<string>`, `<cstdarg>`, `XrdSysPthread.hh`, and compiler format attributes. It is included by nearly every XrdCl subsystem that emits diagnostics.

## Risks

Only the level is atomic; masks, topic map, output replacement, and PID are not guarded. `RegisterTopic` assumes an initialized topic map and can fail if called before any topic exists. `SetOutput` transfers ownership by raw pointer and deletes the previous output. Format attributes help GCC catch mismatches, but only for direct calls with visible format strings.

## Test Signals

Compile-time format checking, runtime severity and mask tests, dynamic topic registration tests, output replacement tests, and threaded logging stress are useful. ABI-sensitive tests should verify enum values and method signatures because logging is a cross-cutting service.
