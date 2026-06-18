# File Research: sources/os/plan9/plan9/sys/src/cmd/cpp/macro.c

Macro definition and expansion engine.

`dodefine` parses object-like, function-like, and variadic macros; `doadefine` handles command-line `-D`/`-U`; `expandrow` scans token rows for expandable names while respecting hidesets and the special `defined` operator. `expand` gathers macro arguments across lines, substitutes arguments, expands arguments except around `##`, applies stringification, performs token pasting, distributes hidesets, and replaces the macro invocation in-place.

Built-in macros expand `__LINE__`, `__FILE__`, `__DATE__`, and `__TIME__`. `__VA_ARGS__` maps to the final variadic argument when present.
