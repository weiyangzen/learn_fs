# sources/sync-backup/git-crypt/git-crypt.cpp

Purpose: program entry point and command dispatcher for the git-crypt CLI.

Important APIs/types/functions: global `argv0`, `print_usage`, `print_version`, `help_for_command`, `help`, `version`, and `main`.

Control flow: `main` records `argv0`, initializes standard streams and crypto, parses global `--help`, `--version`, and `--`, requires a command, then dispatches to public or plumbing command functions. Command-specific `Option_error` is caught close to dispatch so help for the selected command can be printed. Top-level catches translate `Error`, `Gpg_error`, `System_error`, `Crypto_error`, `Key_file` exceptions, and I/O failures into user-facing stderr messages and nonzero exit codes.

State/persistence behavior: only global process state is `argv0` and initialized stream/crypto settings. Persistent mutations are delegated to command handlers.

Dependencies/integration: includes all command, utility, crypto, key, GPG, and option headers. It is the executable target linked by the Makefile.

Risks/test signals: command dispatch must stay aligned with declarations and help text. Tests should cover global option parsing, unknown options/commands, command help, version output, and exception-to-exit-code mapping.
