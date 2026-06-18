# sources/sync-backup/unison/src/fsmonitor.py

Purpose: legacy Python filesystem monitor helper for Unison, supporting Linux pyinotify, macOS FSEvents, and Windows pywin32 `ReadDirectoryChangesW`.

Important functions/classes: logging helpers `mydebug`/`mymesg`; path conversion `relpath`, `my_abspath`, `mangle_filename`, `make_symlinks`, `update_follow`; config parser `conf_parser`; Linux `HandleEvents` and `linuxwatcher`; macOS `filelevel_approx`, `fsevents_callback`, `my_FSEventStreamCreate`, `macosxwatcher`; Windows `win32watcherThread` and `win32watcher`; CLI setup in `__main__`.

Control flow: parses either a root/path list or a Unison profile, resolves local roots/paths/follow directives, truncates the changes file, starts a stdin-watchdog thread that exits when parent closes stdin, then dispatches to the platform watcher. Events are converted to root-relative paths and appended to the configured changes file.

State/persistence: writes change log and macOS state file under the Unison config directory, maintains in-memory symlink-follow maps, and watches recursive directory trees.

Dependencies/integration: Python 2 syntax (`print >>`, `dict.has_key`), pyinotify, PyObjC FSEvents bindings, pywin32, Unison profile semantics, and the external fsmonitor protocol that reads the changes file.

Risks: Python 2 dependency is obsolete. Event coalescing and dropped-event paths can force broad rescans. Symlink-follow handling is partial, especially deletion of followed links. Windows writes binary-mode strings and relies on daemon threads.

Test signals: platform manual tests should verify profile parsing, follow directives, relative path output, dropped-event recovery, stdin-triggered exit, and change-file consumption by Unison.
