# File Research: sources/os/plan9/9front/sys/src/cmd/cpp/macro.c

Macro definition and expansion engine. It handles object-like macros, function-like macros, variadic macros, argument gathering, `#` stringification, `##` token pasting, builtin macros, and hideset propagation.

Important behavior:
- `dodefine()` parses macro names, parameters, duplicate names, ellipsis, and replacement rows.
- `doadefine()` supports command-line `-D` and `-U`.
- `expandrow()` scans token rows and expands normal or builtin macros unless hidden by a token hideset.
- `gatherargs()` can extend token rows across newlines while collecting balanced argument lists.
- `substargs()` expands arguments normally except around stringification/pasting cases.
- `glue()` re-lexes pasted token text and warns if it does not form one valid token.
- Builtins implement `__LINE__`, `__FILE__`, `__DATE__`, and `__TIME__`.
