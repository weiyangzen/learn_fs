# File Research: sources/os/plan9/9front/sys/src/cmd/cpp/nlist.c

Symbol table and command-line setup for cpp. It installs preprocessor keywords and builtin macros, constructs include search paths, parses options, opens input/output, and initializes the source stack.

Important behavior:
- Symbol table is a 128-bucket chained hash keyed by token bytes.
- `quickset`/`quicklook` accelerate “might be macro” checks using first two name bytes.
- Default include paths are `/$objtype/include` and `/sys/include`; `$include` can add more.
- Options include `-I`, `-D`, `-U`, `-M`, `-V`, `-P`, `-N`, `-.`, and ignored `+`.
- `setup()` installs current-directory include behavior and calls `setsource()` for the input.
