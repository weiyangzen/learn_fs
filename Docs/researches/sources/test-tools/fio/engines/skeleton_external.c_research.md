# sources/test-tools/fio/engines/skeleton_external.c

## Purpose
`skeleton_external.c` is a sample external fio ioengine, intended to be compiled as a shared object and loaded through fio's external engine mechanism. It demonstrates the shape of an exported `struct ioengine_ops` without registering via `register_ioengine()`.

## Important APIs, Types, And Functions
`struct fio_skeleton_options` demonstrates engine-private options and includes a padding pointer because fio option offsets cannot be zero. The `options` array defines a dummy `FIO_OPT_STR_SET` option. Stub hooks include `fio_skeleton_init`, `prep`, `queue`, `getevents`, `event`, `cleanup`, `open`, `close`, and zoned block device helpers (`get_zoned_model`, `report_zones`, `reset_wp`, `get_max_open_zones`).

## Control Flow
The file does not perform real I/O. `fio_skeleton_queue()` runs `fio_ro_check()` and returns `FIO_Q_COMPLETED`. `open` and `close` delegate to generic file helpers. Zoned hooks report `ZBD_NONE` or success/no data. The exported `ioengine` symbol is meant to be found via `dlsym(..., "ioengine")`, which is the key difference from built-in engines.

## State And Persistence
No engine state is allocated or persisted. The dummy option toggles an integer in fio's per-engine option area but is otherwise unused.

## Dependencies And Integration Points
The sample depends on fio's public ioengine structures, generic file helpers, option parser structures, and ZBD types from included fio headers. It integrates by exporting `struct ioengine_ops ioengine` rather than constructor-style register/unregister functions.

## Risks
Because this is a skeleton, copying it unchanged creates an engine that silently completes I/O without transferring data. The comments are useful, but the async hooks return no events and would be invalid for a real queued engine without additional state. The sample also does not demonstrate allocation-failure handling or timeout behavior.

## Test Signals
Build it as a shared object with the documented compiler flags and confirm fio can load the `ioengine` symbol and parse `dummy`. Functional tests should be limited to verifying it is a template, not a real data-moving engine.
