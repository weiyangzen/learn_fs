# sources/test-tools/kdevops/scripts/kconfig/symbol.c

## Purpose
`symbol.c` implements Kconfig symbol semantics: type names, visibility calculation, defaults, ranges, choice resolution, user value setters, string validation, symbol lookup/search, reverse dependency warnings, and recursive dependency detection.

## Important APIs, Types, And Functions
Exports include fixed symbols `symbol_yes`, `symbol_mod`, `symbol_no`, global `modules_sym`, `sym_get_type()`, `sym_type_name()`, `sym_get_choice_menu()`, `sym_get_range_prop()`, `sym_choice_default()`, `sym_calc_choice()`, `sym_dep_errors()`, `sym_calc_value()`, `sym_clear_all_valid()`, `sym_tristate_within_range()`, `sym_set_tristate_value()`, `choice_set_value()`, `sym_toggle_tristate_value()`, `sym_string_valid()`, `sym_string_within_range()`, `sym_set_string_value()`, `sym_get_string_default()`, `sym_get_string_value()`, `sym_is_changeable()`, `sym_is_choice_value()`, `sym_lookup()`, `sym_find()`, `sym_re_search()`, `sym_check_deps()`, `prop_get_symbol()`, and `prop_get_type_name()`.

## Control Flow
`sym_calc_value()` is central: it initializes type-appropriate defaults, recalculates visibility/direct/reverse/implied dependencies, applies user values when visible, resolves choices, applies defaults and implies, warns when `select` violates direct dependencies, folds module values to yes for booleans/no-modules, validates ranges, marks menus changed, and invalidates all symbols when `MODULES` changes. Choice resolution prioritizes visible user-selected yes, visible default, first visible unspecified, then least-prioritized visible no. Lookup uses a hashtable, while regex search compiles a case-insensitive regex, evaluates matching symbols, and sorts exact matches before alphabetical results. Dependency checks recurse through expression graphs and print explanatory cycles.

## State And Persistence
Symbol state is in global symbol objects, hashtable entries, per-symbol flags, current/default values, visibility caches, dependency expressions, menus lists, and choice member lists. No direct disk writes occur, but computed `SYMBOL_WRITE` and values drive config output.

## Dependencies And Integration Points
Depends on expression APIs, menu APIs, `conf_set_changed()`, Linux-style hashtable/list utilities, regex, and `xalloc`. `menu.c` builds properties and dependencies; frontends call setters/getters; config I/O reads/writes user defaults and current values.

## Risks And Edge Cases
This is high-risk semantic code: small changes can alter Kconfig resolution globally. Reverse dependencies can force values beyond direct dependencies and only warn unless `KCONFIG_WERROR` is set. String/range validation relies on `strtoll()` and current default symbols. The local source contains duplicated lines in `sym_calc_visibility()`, `sym_clear_all_valid()`, and `sym_lookup()`, likely copy artifacts but not all necessarily compile-breaking.

## Test Signals
Use Kconfig cases for bool/tristate with and without modules, `select`, `imply`, hidden defaults, range checks, hex normalization, invalid strings, choices with user/default/visibility combinations, regex search ordering, recursive dependency errors, and `KCONFIG_WERROR`.
