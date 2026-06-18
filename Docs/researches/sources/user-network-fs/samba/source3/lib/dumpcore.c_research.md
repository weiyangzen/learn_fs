# sources/user-network-fs/samba/source3/lib/dumpcore.c

Purpose: prepares and performs controlled core dumps for Samba processes, including platform-specific core path discovery.

Important APIs/types/functions: `dump_core_setup()`, `dump_core()`, `get_default_corepath()`, Linux core-pattern parsing, and FreeBSD corefile sysctl parsing.

Control flow: setup derives a log/core directory, creates `<logbase>/cores/<progname>` when no OS absolute core path applies, and caches the path. `dump_core()` prevents recursion, checks `lp_enable_core_files()`, becomes root if needed, changes to the core path unless a helper handles dumps, flushes debug logs, marks Linux processes dumpable, resets SIGABRT, and aborts.

State/persistence behavior: static `corepath` and `using_helper_binary` are process-local. Persistent effects are core directories and OS-created core files.

Dependencies/integration: uses Samba config, debug, security, directory, signal, sysctl, and prctl helpers. Called by fatal-error paths.

Risks/test signals: wrong permissions or cwd handling can suppress or leak cores. Tests should cover disabled core policy, Linux pipe/relative/absolute core patterns, non-root privilege transitions, and missing corepath failures.
