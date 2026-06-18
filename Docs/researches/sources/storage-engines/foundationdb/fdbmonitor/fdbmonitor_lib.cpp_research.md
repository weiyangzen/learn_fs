# sources/storage-engines/foundationdb/fdbmonitor/fdbmonitor_lib.cpp

Purpose: implementation library for native `fdbmonitor`. It provides logging, path handling, config value lookup, process maps, child process launching/killing, configuration loading/reconciliation, child output logging, and platform-specific file watch helpers.

Important APIs and functions: logging functions map `Severity` to syslog or structured stderr. Path helpers include `joinPath`, `cleanPath`, `popPath`, `abspath`, `parentDirectory`, and recursive `mkdir`. Process APIs include `getRss`, `start_process`, `kill_process`, `load_conf`, and `read_child_output`. Linux adds `set_watches`; Apple/FreeBSD add kqueue watch helpers.

Control flow: `load_conf` loads `CSimpleIni`, resolves target user/group, kills processes when uid/gid or command config requires restart, updates existing commands, starts new sections named with a dot suffix, and respects fork retry time. `start_process` forks, resets signals, redirects stdout/stderr to pipes, applies envvars/deletions, sets parent-death signal where supported, changes uid/gid, and execs the child.

State and persistence behavior: global maps `id_command`, `pid_id`, and `id_pid` hold live supervisor state. The library mutates child processes and logs output but does not persist config itself. RSS reads `/proc/<pid>/statm` on Linux.

Dependencies and integration points: depends on POSIX APIs, syslog, passwd/group lookup, SimpleIni, FoundationDB version macros, Flow error types in some utility paths, and platform watch primitives.

Risks: `execv` failure exits child with status 0, which may be interpreted as successful exit by parent restart logging. `read_child_output` logs partial reads line-by-line but may split long lines. `load_conf` mutates maps while iterating derived lists carefully, but this area is lifecycle-sensitive.

Test signals: `fdbmonitor_tests.cpp` covers path normalization/resolution and environment parsing. Process launch, uid/gid changes, config reload, and watch behavior have limited unit coverage.
