# sources/test-tools/fio/io_ddir.h

## Purpose
Defines fio's I/O direction enums, job direction bitmasks, and helper macros used throughout scheduling, accounting, logging, and option validation.

## Important APIs, Types, and Functions
`enum fio_ddir` defines read, write, trim, sync variants, wait, invalid, timeout, and direction counts. `for_each_rw_ddir` iterates read/write/trim. `io_ddir_name`, `ddir_sync`, `ddir_rw`, `ddir_str`, and `ddir_rw_sum` provide name and classification helpers. `enum td_ddir` defines job direction combinations such as `TD_DDIR_RANDRW` and `TD_DDIR_RANDTRIMWRITE`. Macros such as `td_read`, `td_write`, `td_trim`, `td_rw`, `td_random`, `td_trimwrite`, and `td_randtrimwrite` inspect `thread_data` options.

## Control Flow
There is no standalone execution. The helpers are inline decision points used by I/O generation, engine dispatch, initialization fixups, and statistics.

## State and Persistence Behavior
No state is stored. The macros read `td->o.td_ddir` and file random-map state.

## Dependencies and Integration Points
Used by `io_u.c`, `init.c`, `ioengines.c`, stats, verify, trim, and file setup paths. It relies on `fio_file_axmap()` being visible where `file_randommap()` is used.

## Risks
Array order must stay synchronized with `DDIR_*` values. `io_ddir_name()`'s static name list appears shorter/misaligned for later sync values, so any enum additions need careful review. `ddir_str()` indexes by bitmask value and only supports specific combinations.

## Test Signals
Compile-time and unit coverage should assert expected strings/classification for each direction and common `td_ddir` combinations. Full fio job tests indirectly validate direction macros.
