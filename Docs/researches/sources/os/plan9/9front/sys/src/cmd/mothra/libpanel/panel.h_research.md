# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/panel.h

Public libpanel API and data model.

Key behavior:
- Defines `Scroll`, `Rtext`, `Panel`, and `Idol`.
- `Panel` includes public layout fields and private tree, draw target, flags, state, scroll links, kind-specific data, and method callbacks.
- Defines layout flags (`PACK`, `FILL`, `PLACE`, `EXPAND`, `FIXED`, `MAX`, `BITMAP`, `IGNORE`, `USERFL`), priorities, mouse `OUT`, and rich-text flags.
- Declares core lifecycle/layout/draw/input/scroll/snarf APIs and constructors for all widgets.
- Declares rich-text, idol-list, and snarf helper APIs.

Important dependencies: Plan 9 `draw` and event types.

Notable risks:
- Struct fields marked private are still visible and used by implementation and callers.
- Header declares broad APIs; implementation files assume global `font`, `screen`, and `display`.
