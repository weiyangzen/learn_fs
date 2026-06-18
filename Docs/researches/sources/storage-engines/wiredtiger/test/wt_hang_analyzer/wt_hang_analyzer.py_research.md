# sources/storage-engines/wiredtiger/test/wt_hang_analyzer/wt_hang_analyzer.py

## Purpose
`wt_hang_analyzer.py` is a standalone diagnostic tool for collecting debugger output, and optionally core/minidump files, from interesting WiredTiger test processes during timeouts. It was designed for Evergreen-style hang investigation and supports Linux primarily, with Windows and LLDB/Darwin code paths present but Darwin intentionally disabled.

## Important APIs and classes
Important helpers include `LoggerPipe`, `call`, `callo`, `find_program`, `get_process_logger`, `get_hang_analyzers`, `check_dump_quota`, `pname_match`, `avoid_asan_dump`, and `main`. Platform adapters are `WindowsDumper`, `WindowsProcessList`, `LLDBDumper`, `DarwinProcessList`, `GDBDumper`, and `LinuxProcessList`. Command-line options select process-name contains/exact filters, explicit PIDs, core dumping, maximum dump size, and debugger output destinations.

## Control flow and behavior
`main` logs Python/OS/user context, parses options, chooses process and debugger adapters, enumerates processes, filters out itself, and iterates targets. For each process it tries to reduce ASAN-heavy core mappings through `/proc/<pid>/coredump_filter`, builds a per-process logger, and runs the platform dumper. Linux invokes `gdb` with batch commands for shared libraries, thread lists, all backtraces, scheduler locking, optional `gcore`, and quit. Windows invokes `cdb`; LLDB writes commands to a temporary file and sources them.

## State, dependencies, and integration
The script writes debugger logs named `debugger_<process>_<pid>.log` when file output is enabled and dump files named by process/pid/extension when core dumping is enabled. It depends on platform tools (`ps`, `gdb`, `cdb`, `lldb`), Python stdlib process/logging/threading modules, and Windows `pywin32` imports on Windows. It integrates with Evergreen or manual timeout triage workflows.

## Risks and test signals
Risks include debugger attach permissions, deprecated `platform.linux_distribution`, broad default matching that includes Python/test processes, command failures propagating as trapped exceptions, and Linux-specific `/proc` logic in `avoid_asan_dump`. Signals are useful per-process backtraces, nonzero exit when debugger invocations fail, quota-limited core creation, missing PID warnings, unsupported-platform warnings, and no subprocess pipe deadlocks due to `LoggerPipe`.
