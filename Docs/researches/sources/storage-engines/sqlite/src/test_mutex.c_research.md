# sources/storage-engines/sqlite/src/test_mutex.c

## Purpose

`test_mutex.c` exposes SQLite mutex configuration, initialization, locking, counters, and failure simulation to Tcl tests.

## Important APIs, types, and functions

The local `struct sqlite3_mutex` wraps a real mutex pointer and type. Global `g` stores install/init flags, failure toggles, saved real mutex methods, counters by mutex type, and static wrapper mutexes. Wrapper methods are `counterMutex*`. Tcl commands include `sqlite3_shutdown`, `sqlite3_initialize`, `sqlite3_config`, `install_mutex_counters`, `read_mutex_counters`, `clear_mutex_counters`, `alloc_dealloc_mutex`, and static/db mutex enter/leave commands.

## Control flow

Installing counters captures real mutex methods and installs wrapper methods with `SQLITE_CONFIG_MUTEX`. Allocation wraps dynamic mutexes with heap objects and static mutexes with entries in `g.aStatic`. Enter/try increments counters before delegation; linked Tcl variables can force init failure or try-lock `SQLITE_BUSY`. Uninstall restores saved methods.

## State and persistence behavior

State is process-global and affects SQLite's mutex subsystem while installed. Counters persist until cleared. Db mutex enter/leave commands directly lock connection mutexes and must be balanced by tests.

## Dependencies and integration points

It depends on Tcl, SQLite mutex/config APIs, `sqliteInt.h`, `sqlite3ErrName()`, and test pointer helpers. It integrates with threading-mode, initialization-failure, static mutex, and db mutex tests.

## Risks and test signals

Configuration must happen at safe SQLite lifecycle points. Unbalanced lock commands can deadlock. Counters count attempts, including forced failed try-locks. Signals include named counter lists, forced busy/init errors, allocation pointer output, and expected config return names.
