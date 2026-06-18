# File Research: sources/local-fs/xfsprogs/db/command.h

Purpose: defines the public command registration and dispatch interface.

Key contents:
- Defines `cfunc_t` for command handlers and `helpfunc_t` for help callbacks.
- Defines `cmdinfo_t` with name, alternate name, handler, argument limits, stack-push capability, argument string, one-line description, and help callback.
- Declares global `cmdtab` and `ncmds`.
- Declares `add_command`, `command`, `find_command`, and `init_commands`.
- Declares init functions implemented outside module-specific headers, such as `convert_init`, `btdump_init`, `info_init`, `btheight_init`, `timelimit_init`, `namei_init`, `iunlink_init`, `bmapinflate_init`, and `rdump_init`.

Interactions:
- Included by command implementations throughout `db/`.
- Provides the common ABI by which `command.c` discovers and invokes commands.

Risks/notes:
- Header assumes surrounding includes provide command implementation dependencies; it only defines the registry-level types.
