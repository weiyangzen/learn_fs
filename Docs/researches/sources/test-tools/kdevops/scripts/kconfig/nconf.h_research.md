# sources/test-tools/kdevops/scripts/kconfig/nconf.h

## Purpose
`nconf.h` is the shared header for the ncurses Kconfig frontend. It centralizes system includes, min/max macros, color attribute externs, function-key identifiers, callback typedefs, and GUI helper prototypes.

## Important APIs, Types, And Functions
It declares the `function_key` enum (`F_HELP` through `F_EXIT`), all `attr_*` globals, `extra_key_cb_fn`, and prototypes for color setup, text helpers, button/input dialogs, scroll windows, and refresh orchestration.

## Control Flow
There is no runtime control flow. The header defines compile-time contracts used by `nconf.c` and implemented by `nconf.gui.c`.

## State And Persistence
The declared `attr_*` variables are global process state initialized by `set_colors()`. No persistent storage is involved.

## Dependencies And Integration Points
Includes standard C headers and ncurses headers `ncurses.h`, `menu.h`, `panel.h`, and `form.h`. Build integration depends on `nconf-cfg.sh` producing matching library flags. The `extra_key_cb_fn` type lets scroll windows call back into search jump logic.

## Risks And Edge Cases
The `max` and `min` macros use GNU statement expressions and `typeof`, so they are not strict ISO C. Headers expose many globals, making initialization order important. Consumers must link against the full ncurses menu/panel/form stack.

## Test Signals
Compile both `nconf.c` and `nconf.gui.c` with the detected flags; run basic UI smoke tests and confirm all declared attributes are initialized before use.
