# File Research: sources/os/bsd/netbsd-src/lib/libmenu/userptr.c

Implements simple item/menu user-pointer setters and getters. Passing `NULL` for an item or menu targets the respective default object (`_menui_default_item` or `_menui_default_menu`).

Important dependencies: `<menu.h>`, `<stdlib.h>`, `<string.h>`, and extern definitions from `menu.c`/`item.c`.

The user pointers are stored as `char *`; ownership is not managed by libmenu.
