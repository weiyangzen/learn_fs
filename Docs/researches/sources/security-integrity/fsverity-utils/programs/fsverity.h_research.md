# sources/security-integrity/fsverity-utils/programs/fsverity.h

Purpose: This private CLI header declares command structures, option constants, shared utility prototypes, and interfaces between the main dispatcher and subcommands.

Important APIs and types: It defines `struct fsverity_command`, command handler prototypes, file descriptor wrappers, option enum values, usage/error helpers, parsing helpers, and full-read/write/open utilities.

Control flow and state: No runtime state exists in the header, but it defines shared conventions for status codes, option parsing, and resource cleanup.

Dependencies and integration points: Included by every program command source and shared `programs/utils.c`.

Risks and test signals: Misdeclared handler signatures or option constants can break dispatch or parsing. Signals are successful compile, subcommand invocation, and common utility tests through CLI workflows.
