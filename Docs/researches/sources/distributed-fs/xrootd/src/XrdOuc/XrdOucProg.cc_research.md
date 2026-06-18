<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucProg.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucProg.cc

Purpose: Implements a wrapper for configured external programs or inline procedures, with one-shot run and long-lived feed modes.

APIs and control flow: `Setup()` parses a command string with `XrdOucUtils::argList()`, optionally records an inline procedure, and verifies executable access for external programs. `Run()` variants append extra args, optionally set environment through `XrdOucStream`, execute, drain output, capture the first output line, and translate wait status into negative errno-style returns. `Start()` creates a persistent stream and starts the command. `Feed()` serializes writes with a static mutex, restarts a dead process, retries failed writes once after restart, and reports errors.

State and persistence: Owns parsed argument buffer/argv, optional stream, inline procedure pointer, and error fd. Long-lived process state is managed through `XrdOucStream`.

Dependencies and integration: Uses `XrdOucStream`, `XrdOucEnv`, `XrdOucUtils`, `XrdSysError`, POSIX process/wait APIs, and Win32 compatibility.

Risks and test signals: `Feed()` uses a single static mutex across all program instances, and restart semantics can duplicate input attempts. Tests should cover setup parsing, missing executables, inline procedures, env passing, output capture trimming, signal exits, and persistent restart/feed behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucProg.cc -->
