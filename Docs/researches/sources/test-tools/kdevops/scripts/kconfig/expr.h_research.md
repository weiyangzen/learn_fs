# sources/test-tools/kdevops/scripts/kconfig/expr.h

## Purpose
`expr.h` defines the core Kconfig data model for tristate values, dependency expressions, configuration symbols, properties, menus, and jump keys, plus the public expression API.

## Important APIs, Types, And Functions
Key types are `tristate`, `enum expr_type`, `struct expr`, `struct expr_value`, `struct symbol_value`, `enum symbol_type`, `struct symbol`, `enum prop_type`, `struct property`, `struct menu`, and `struct jump_key`. Important flags include `SYMBOL_CONST`, `SYMBOL_VALID`, `SYMBOL_WRITE`, `SYMBOL_YAML`, `SYMBOL_WRITTEN`, `SYMBOL_DEF_USER`, and menu flag `MENU_CHANGED`. Iteration macros include `for_all_properties()`, `for_all_defaults()`, and `for_all_prompts()`. Expression prototypes expose allocation, simplification, evaluation, dependency query, and printing functions.

## Control Flow
The header has no runtime flow but defines the object graph traversed by parser, menu, symbol, conf, and expression modules. Symbols own lists of menu definitions and properties; menus form a parent/child/next tree and may reference symbols; properties link prompts/defaults/selects/ranges back to menus.

## State And Persistence
The structures hold all in-memory Kconfig state: current symbol values, user/default values, visibility, direct and reverse dependencies, menu hierarchy, source locations, help text, and frontend data. Persistence is implemented elsewhere by reading/writing these fields.

## Dependencies And Integration Points
It includes `list_types.h` and is included by `lkc.h` and almost every Kconfig implementation file. Changes to these structures affect parser, frontend, config I/O, and expression logic.

## Risks And Test Signals
Flag bit compatibility is important because many modules test and mutate the same fields. `SYMBOL_DEF3` and `SYMBOL_DEF4` comments appear to reference old names (`S_DEF_3`, `S_DEF_4`) while the enum uses `S_DEF_DEF3` and `S_DEF_DEF4`. Structural changes require full Kconfig parser, conf, menuconfig, and serialization tests.
