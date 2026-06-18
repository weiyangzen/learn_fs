# sources/test-tools/fio/options.h

## Purpose
`options.h` exposes fio's option table interface to the rest of the program. It declares the global option capacity, option registration/mutation helpers, cleanup helpers, filename-list utilities, and the option-set query macro used by runtime code to distinguish defaults from explicit user input.

## Important APIs, Types, and Functions
The header declares `FIO_MAX_OPTS`, `fio_options`, `client_sockaddr_str`, `add_option()`, `invalidate_profile_options()`, `add_opt_posval()`, `del_opt_posval()`, `fio_options_free()`, `fio_dump_options_free()`, `get_next_str()`, `get_max_str_idx()`, `get_name_by_idx()`, `set_name_idx()`, `__fio_option_is_set()`, `fio_option_mark_set()`, `find_option()`, `find_option_c()`, `fio_option_find()`, and `fio_get_kb_base()`. `fio_option_is_set()` wraps `offsetof(struct thread_options, name)` and calls the offset-based lookup.

## Control Flow
Consumers include this header to find or mutate registered options and to ask whether a field was explicitly set. `o_match()` performs name-or-alias comparisons for option-table scans. Filename helpers declared here are implemented in `options.c` and are used when fio expands colon-separated file or directory lists.

## State and Persistence
The header itself owns no storage other than extern declarations. It grants access to the process-global `fio_options` array and `client_sockaddr_str`, and its macros query `thread_options.set_options` indirectly.

## Dependencies and Integration Points
It depends on `parse.h`, `lib/types.h`, `struct fio_option`, and `struct thread_options`. It is a bridge between parser internals, job setup, profiles, ioengines, and runtime code that needs explicit-option detection.

## Risks and Edge Cases
`fio_option_is_set()` relies on field names existing in `struct thread_options` and on `options.c` finding all options with matching `off1`; duplicate offsets are supported but can make the answer true because of any aliasing option. `FIO_MAX_OPTS` bounds dynamic additions and must remain large enough for profiles and build-time options.

## Test Signals
Signals include successful compilation of all users, explicit-vs-default checks for fields with aliases, option addition near capacity, profile invalidation, and filename-list parsing of escaped colons.
