# File Research: sources/virtualization/nvme-cli/plugin.c

- Purpose: generic plugin and command dispatcher for nvme-cli.
- Built-ins: implements `version`, `help`, usage printing, and general command/plugin help.
- Dispatch behavior: parses global help/version options before subcommand parsing, supports exact command names, aliases, unique command abbreviations, extension plugin names, and legacy combined `plugin-command` invocation.
- Help behavior: tries to open command-specific man pages with `man`, then falls back to generated command help.
- Extension listing: built-in plugin help lists installed extension plugins; extension plugin help lists only that plugin’s commands.
- Error behavior: invalid subcommands return `-ENOTTY` and print an error.
