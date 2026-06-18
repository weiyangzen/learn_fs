# sources/sync-backup/git-crypt/parse_options.hpp

Purpose: declares the lightweight subcommand option parser.

Important APIs/types/functions: `struct Option_def`, `typedef Options_list`, `parse_options`, and `struct Option_error`.

Control flow: headers define option descriptors for either boolean flags or string-valued options. Runtime parsing is implemented in `parse_options.cpp`.

State/persistence behavior: option parsing writes directly into caller-owned variables and returns an argv index. No persistent state.

Dependencies/integration: used throughout command handlers to keep command parsing uniform.

Risks/test signals: `Option_def` can represent only bool or string value options; future option types require extension. Tests should check that thrown `Option_error` includes the right option name and message for CLI reporting.
