# sources/security-integrity/fsverity-utils/programs/fsverity.c

Purpose: This is the main entrypoint and command dispatcher for the `fsverity` CLI.

Important APIs and functions: It defines the command table, help/usage rendering, option dispatch, version behavior, and main argument routing to `digest`, `enable`, `measure`, `sign`, and `dump_metadata` command handlers.

Control flow and state: `main()` identifies the subcommand, adjusts argc/argv, invokes the selected handler, and returns its status. Global state is limited to command metadata and process-level error output behavior.

Dependencies and integration points: Integrates all `programs/cmd_*.c` files, shared CLI utilities, version constants, and build-time feature availability.

Risks and test signals: Risks include command-name compatibility, usage text drift, and return-code conventions. Signals include `fsverity --help`, subcommand usage tests, unknown command errors, and version output checks.
