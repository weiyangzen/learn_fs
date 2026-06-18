<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/keyctl.h -->
# sources/security-integrity/keyutils/keyctl.h

## Purpose

`keyctl.h` is the shared internal interface for the `keyctl` executable modules. It defines the command dispatch structure and declares common frontend helpers plus the watch and built-in test action entry points.

## Important APIs, Types, and Functions

`struct command` carries a noreturn action pointer, command name, and usage format. The `nr` macro applies `__attribute__((noreturn))`. Exported internal declarations include `do_command()`, `format()`, `error()`, `get_key_id()`, `act_keyctl_test()`, `act_keyctl_watch()`, `act_keyctl_watch_add()`, `act_keyctl_watch_rm()`, `act_keyctl_watch_session()`, and `act_keyctl_watch_sync()`.

## Control Flow

This header has no runtime control flow. It lets `keyctl.c` dispatch commands implemented in `keyctl_testing.c` and `keyctl_watch.c` through one command table.

## State and Persistence Behavior

No state is stored here. The declarations expose functions that mutate process or kernel keyring state elsewhere.

## Dependencies and Integration Points

It depends on `key_serial_t` being visible from `keyutils.h` before inclusion. It is included by `keyctl.c`, `keyctl_testing.c`, and `keyctl_watch.c`, making it the coupling point for command-line module integration.

## Risks and Edge Cases

The header omits include guards, so duplicate inclusion would redeclare symbols if translation units include it more than once. The noreturn function pointer type must stay consistent with all action implementations or compiler diagnostics and undefined assumptions can follow.

## Test Signals

Successful compilation of the three `keyctl` modules and use of `--test` plus `watch*` commands confirms this shared dispatch contract.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/keyctl.h -->
