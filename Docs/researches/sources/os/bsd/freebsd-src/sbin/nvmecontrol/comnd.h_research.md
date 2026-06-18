# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/comnd.h

Header for the `nvmecontrol` command framework.

Key contents:
- Defines `arg_type` enum for supported option/argument value types.
- Defines `struct opts`, `struct args`, and `struct cmd`.
- Provides `CMD_COMMAND` and `CMD_SUBCOMMAND` constructor macros.
- Declares command registration, dispatch, parsing, help, initialization, and module loading APIs.

Research notes:
- The framework is simple and plugin-friendly, but command option state is static/global rather than per-dispatch context despite `ctx_size` existing in `struct cmd`.
