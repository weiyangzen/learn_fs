# sources/test-tools/kdevops/scripts/kconfig/mnconf-common.h

## Purpose
`mnconf-common.h` declares shared search navigation helpers used by both menuconfig frontends and by menu relation rendering.

## Important APIs, Types, And Functions
It defines `struct search_data { struct list_head *head; struct menu *target; }`, declares `extern int jump_key_char`, and prototypes `next_jump_key()`, `handle_search_keys()`, and `get_jump_key_char()`.

## Control Flow
The header has no control flow, but it establishes the callback contract: scrollable windows pass key input plus text viewport offsets and a `search_data` pointer; the implementation may set `target` and return nonzero to request a jump.

## State And Persistence
The shared global `jump_key_char` is process-local UI rendering state. No persistence is defined.

## Dependencies And Integration Points
Includes `<stddef.h>` and `<list_types.h>`. It forward-uses `struct menu` without defining it, relying on Kconfig consumers to include full menu declarations where needed.

## Risks And Edge Cases
The public global means multiple search renderers in the same process must reset and use it carefully. The callback data is untyped `void *` at call sites, so misuse can crash.

## Test Signals
Header-level validation is compile coverage for `mconf.c`, `nconf.c`, `menu.c`, and `mnconf-common.c`, plus runtime search jump behavior.
