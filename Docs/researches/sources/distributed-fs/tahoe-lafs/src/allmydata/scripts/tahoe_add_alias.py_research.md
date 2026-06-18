# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_add_alias.py

## Purpose
Implements alias management commands: add an existing directory cap, create a new Tahoe directory and alias it, and list configured aliases.

## APIs, Types, And Control Flow
`add_alias` validates alias characters, rejects duplicates, normalizes the provided cap as a directory URI, and appends it to `private/aliases`. `create_alias` performs the same validation, POSTs `uri?t=mkdir` to the gateway, then records the returned URI. `list_aliases` loads alias details, optionally emits JSON, and can show read-only caps. Helpers include `add_line_to_aliasfile`, `show_output`, `_get_alias_details`, and `_escape_format`.

## State, Persistence, And Integration
Writes `private/aliases` through a temporary file plus `move_into_place`; reads aliases through `common.get_aliases`. It integrates with URI parsing, `common_http.do_http`, JSON byte helpers, and CLI option classes in `cli.py`.

## Risks And Test Signals
Risks include non-atomic read-modify-write races on the alias file, silent alias-read errors inherited from `get_aliases`, output encoding complexity, and no creation of parent `private` if the node directory is malformed. Test signals are `allmydata/test/cli/test_alias.py` and `test_create_alias.py`.
