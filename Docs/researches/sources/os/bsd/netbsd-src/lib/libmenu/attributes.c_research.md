# File Research: sources/os/bsd/netbsd-src/lib/libmenu/attributes.c

Implements menu display attribute setters/getters: foreground, background, greyed-out/nonselectable attribute, and pad character. Passing `NULL` targets the global `_menui_default_menu`; otherwise the specific `MENU` is modified.

Important dependencies: `<menu.h>` and external `_menui_default_menu`.

Notable issue: getter return types for `menu_fore()`, `menu_back()`, and `menu_grey()` are `char` even though the stored fields are `attr_t`, which may truncate attributes on implementations where `attr_t` is wider.
