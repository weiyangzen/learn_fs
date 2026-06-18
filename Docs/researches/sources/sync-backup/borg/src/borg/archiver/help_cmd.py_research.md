# sources/sync-backup/borg/src/borg/archiver/help_cmd.py

## Purpose

`help_cmd.py` implements Borg's extra help system, including long-form help topics for patterns, archive matching, placeholders, and compression, plus command-help routing. The source was read as a complete 563-line file.

## Important APIs, Types, and Functions

`HelpMixIn.helptext` is a class-level dictionary populated with nanorst/reStructuredText-like text for `"patterns"`, `"match-archives"`, `"placeholders"`, and `"compression"`. `do_help()` selects between top-level parser help, topic help rendered through `rst_to_terminal()`, command parser help, command epilog-only output, command usage-only output, and an error listing known commands/topics. `do_subcommand_help()` and `do_maincommand_help` print parser help. `build_parser_help()` registers `borg help` with `--epilog-only`, `--usage-only`, and optional `TOPIC`.

## Control Flow

The help command receives the main parser and args. Without a topic it prints main parser help. If the topic is in `helptext`, it renders that topic for terminal output. If the topic matches a registered subcommand, it prints either the command epilog, usage/help with epilog suppressed, or full help. Unknown topics call `parser.error()` with suggestions. The parser builder simply adds the `help` subcommand and options.

## State and Persistence Behavior

There is no persistent state. The command mutates a command parser object transiently when `--usage-only` sets `commands[topic].epilog = None` before printing help. All output is terminal text.

## Dependencies and Integration Points

The module depends on Borg's `ArgumentParser`, shared constants, and `rst_to_terminal()` conversion. Its topic names are also consumed by `completion_cmd.py`, which completes help topics from `self.helptext.keys()`. Topic text documents parser behavior implemented across `create`, `extract`, `delete`, `prune`, and related commands.

## Risks and Edge Cases

Static help text can drift from parser defaults, validator behavior, or feature support. `--usage-only` mutates the parser's epilog field for the current process, which is normally harmless for one-shot CLI use but could affect repeated parser use in tests. Long topic strings include examples, escaping rules, and platform notes that need careful maintenance when path or pattern behavior changes.

## Test Signals

Tests should assert every expected topic renders, unknown topics include command/topic suggestions, command topics support full help, epilog-only and usage-only modes work, completion sees the same topic names, and representative text snippets for pattern/compression behavior stay in sync with parser choices.
