# sources/user-network-fs/samba/source3/registry/reg_import.c

## Purpose
`reg_import.c` adapts parsed `.reg` events to registry mutation callbacks. It bridges `reg_parse` output to several possible value-setting APIs: raw blobs, `struct registry_value`, or `struct regval_blob`.

## Important APIs, Types, And Functions
The local `struct reg_import` embeds `struct reg_parse_callback` first, stores a `struct reg_import_callback`, and tracks the current `open_key`. `reg_import_adapter()` is the public constructor. Event handlers include `reg_parse_callback_key()`, `reg_parse_callback_val()`, `reg_parse_callback_val_registry_value()`, `reg_parse_callback_val_regval_blob()`, `reg_parse_callback_val_del()`, and `reg_parse_callback_comment()`.

## Control Flow
On a parsed key, the adapter closes any currently open key. Delete-key events call `deletekey()` and treat `WERR_FILE_NOT_FOUND` as success. Create/open events call `createkey()` and store the returned key handle. Parsed values are forwarded to the configured setter variant based on `setval_type`. Value deletes call `deleteval()`. Comments are logged and ignored.

## State And Persistence
Persistent changes are performed by user-supplied callbacks. The adapter owns only transient parser state and the current open-key pointer. Missing open/close/create/delete callbacks are replaced with no-op functions, but set-value callbacks are asserted for active setter modes.

## Dependencies And Integration Points
It depends on `reg_parse.h`, `reg_import.h`, `registry.h`, and `reg_objects.h`. It is designed to be passed as a `reg_parse_callback` to `reg_parse_file()` or `reg_parse_fd()`.

## Risks And Test Signals
The adapter assumes values appear after a successful key event; tests should check parser enforcement and callback behavior when `open_key` is null. Because missing set-value callbacks trigger assertions, misconfigured import code can abort rather than return an error. Tests should cover all three setter modes, key close ordering, delete-missing-as-success, value delete errors, and memory ownership for temporary `DATA_BLOB` and `regval_blob` objects.
