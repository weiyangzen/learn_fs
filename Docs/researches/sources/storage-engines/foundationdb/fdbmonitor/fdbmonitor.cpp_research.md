# sources/storage-engines/foundationdb/fdbmonitor/fdbmonitor.cpp

Purpose: native process monitor executable for FoundationDB. It parses CLI options, locks a singleton pid file, watches configuration paths, loads process commands, supervises child processes, handles signals, relays child output, and enforces Linux RSS limits.

Important APIs and functions: `main` uses `SimpleOpt` options `--conffile`, `--lockfile`, `--loggroup`, `--daemonize`, and help flags. Platform signal handlers update `exit_signal` and `child_exited`. It calls library functions such as `joinPath`, `parentDirectory`, `mkdir`, `set_watches`, `load_conf`, `read_child_output`, `getRss`, and `kill_process`.

Control flow: startup canonicalizes the config path, configures inotify or kqueue, optionally daemonizes, locks/writes the lockfile, blocks signals, and enters a loop. Reloads rebuild watches and call `load_conf`. The loop waits on child pipes, config watch events, signals, fork retry deadlines, and RSS-check deadlines. SIGCHLD triggers wait/restart; SIGHUP reloads and resets delays; SIGINT/SIGTERM kills children, waits, unlinks lockfile, and exits.

State and persistence behavior: persists the pid in the lockfile and may daemonize. Runtime state is held in global process maps from `fdbmonitor_lib.cpp`. Configuration changes can kill/restart children. Linux RSS violations kill processes and rely on SIGCHLD restart handling.

Dependencies and integration points: depends on POSIX process/signal/file APIs, inotify on Linux, kqueue on Apple/FreeBSD, `fdbclient/versions.h`, and `fdbmonitor_lib`.

Risks: single-threaded event-loop correctness depends on careful signal masking and fd-set maintenance. Symlink and missing-path watch logic is complex. `wait(nullptr)` during shutdown relies on SIGCHLD ignored semantics.

Test signals: only indirectly covered by `fdbmonitor_tests`; full process supervision, signal, inotify/kqueue, daemon, and RSS behavior require integration/runtime tests.
