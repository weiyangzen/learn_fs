<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/semodule/semodule.c -->
# sources/security-integrity/selinux/policycoreutils/semodule/semodule.c

## Purpose
Implements the SELinux module-store command-line client for installing, removing, listing, extracting, enabling/disabling, rebuilding, refreshing, and reloading policy modules.

## Important APIs, Types, And Functions
Core types are `enum client_modes` and `struct command`. Important helpers are `cleanup()`, `set_store()`, `set_store_root()`, `create_signal_handlers()`, `parse_command_line()`, `set_mode()`, and `hash_module_data()`. It uses libsemanage handles, transactions, module keys/info, module install/remove/extract/list/set-enabled APIs, checksum computation, store selection/root APIs, reload/rebuild flags, and CIL log level control.

## Control Flow
`main()` handles `genhomedircon` argv0 compatibility by replacing argv with `-B -n`, parses global options and ordered commands, creates or uses a semanage handle, selects store/store root, enables store creation, connects, optionally reloads, begins a transaction for build/refresh, sets default priority, executes each queued command, accumulates whether a commit is needed, applies reload/rebuild/dontaudit/tunables/cache flags, commits, disconnects, and cleans up.

## State And Persistence
Install/remove/enable/disable/build operations mutate the semanage policy store and may reload the active policy unless `-n/-N` suppresses reload. Extract writes a module file in the current directory using exclusive create. List operations are read-only.

## Dependencies And Integration Points
It is the user-facing bridge to libsemanage's direct policy store, CIL compiler behavior, module cache, store priority model, and `genhomedircon` rebuild logic.

## Risks And Edge Cases
Mode ordering matters because priority and CIL/HLL extraction mode are commands in the same queue. Signal handlers drop termination signals, relying on cleanup after API calls. Extract refuses to overwrite files, which avoids clobber but can surprise scripts. Store path/root mistakes affect persistent policy.

## Test Signals
Test ordered multi-command sequences, priority validation, install/remove/enable/disable commits, no-reload, full and standard listing with checksums, extract CIL/HLL output and no overwrite, refresh/rebuild flags, alternate store/config paths, and `genhomedircon` argv0 behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/semodule/semodule.c -->
