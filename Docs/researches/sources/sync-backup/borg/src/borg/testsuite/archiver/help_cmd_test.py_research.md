# sources/sync-backup/borg/src/borg/testsuite/archiver/help_cmd_test.py

Purpose: tests Borg command help generation, topic rendering, parser discovery, and per-command `--help` invocations.

Important APIs/types/functions: `get_all_parsers` builds `Archiver(prog="borg")` and `Archiver(prog="borgfs")` parsers, recursively discovers subcommand parsers from argparse subparser actions, and returns a command-to-parser map. Tests use `RstToTextLazy`, `rst_to_terminal`, `cmd`, and `exec_cmd`.

Control flow: usage/help tests invoke root help, topic help, command help, epilog-only, and usage-only variants. Formatting tests ensure lazy RST epilogs carry source RST and all helptext topics render to terminal text. Main help test asserts additional topic names appear. Parametrized command help test invokes every discovered command's `--help`, with a special borgfs parser path, and asserts usage appears without traceback.

State and persistence behavior: parser construction is in-memory. No repository state is required.

Dependencies and integration points: covers parser construction for Borg and borgfs, help topic dictionary, nanorst rendering, custom subcommand action discovery, and top-level command invocation.

Risks: introspects argparse internals by checking class-name strings and `_actions`; parser implementation changes may require updates. Exact help topic names are part of the tested user interface.

Test signals: validates help remains renderable for every command/topic and does not crash with traceback.
