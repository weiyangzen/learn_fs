# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/error_message.c

## Purpose
`error_message.c` resolves numeric `errcode_t` values into human-readable strings from system errno tables, static com_err tables, and dynamically added tables.

## Important APIs, Types, and Functions
Public globals are `_et_list` and `_et_dynamic_list`; public functions are `et_list_lock()`, `et_list_unlock()`, `error_message()`, `add_error_table()`, `remove_error_table()`, and `add_to_error_table()`. Internal helpers manage semaphores, secure debug env handling, and debug output.

## Control Flow
`error_message()` splits a code into table base and offset, handles system errno for base zero, scans static then dynamic lists under a lock, and formats `Unknown code <table> <offset>` into a thread-local buffer when unresolved. Add/remove operations allocate or unlink dynamic list nodes and optionally log debug messages from `COMERR_DEBUG`.

## State, Persistence, Dependencies, Risks, and Test Signals
State includes global static/dynamic table lists, optional semaphore lock, debug mask/file, and thread-local unknown-code buffer. Dependencies include `strerror`, optional `sem_init`, secure getenv/prctl logic, and `error_table_name()`. Risks include static table matching only low 24 bits, lock setup/destructor portability, `init_error_table()` bypassing locks, and short unknown-code buffer assumptions. Test signals are correct system errno text, generated table lookup, add/remove behavior, and debug environment behavior in non-privileged processes.
