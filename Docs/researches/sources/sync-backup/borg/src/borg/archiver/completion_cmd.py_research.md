# sources/sync-backup/borg/src/borg/archiver/completion_cmd.py

## Purpose

`completion_cmd.py` implements `borg completion`, generating shell completion scripts through `shtab` and augmenting generated output with Borg-specific dynamic completions for bash and zsh. It supports completions for archive names and IDs, tags, sort keys, files-cache modes, compression specs, chunker parameters, timestamps, sizes, paths, and help topics. The source was read as a complete 763-line file.

## Important APIs, Types, and Functions

The major constants are `BASH_PREAMBLE_TMPL` and `ZSH_PREAMBLE_TMPL`, which embed shell functions such as `_borg_complete_archive`, `_borg_complete_tags`, `_borg_complete_sortby`, `_borg_complete_filescachemode`, `_borg_complete_compression_spec`, `_borg_complete_chunker_params`, `_borg_complete_relative_time`, `_borg_complete_timestamp`, `_borg_complete_file_size`, and `_borg_help_topics`. `_attach_completion()` recursively tags argparse actions whose `type` matches a target validator/type. `_attach_help_completion()` recursively tags help topic arguments. `CompletionMixIn.do_completion()` rebuilds the full parser, attaches custom completion metadata, formats shell preambles with `partial_format()`, and prints `parser.get_completion_script()`. `build_parser_completion()` wires the `completion SHELL` subcommand.

## Control Flow

At runtime, `do_completion()` calls `self.build_parser()` to obtain the complete command tree. It walks all nested subcommands and attaches shell completion hooks to specific action types: `archivename_validator`, `SortBySpec`, `FilesCacheMode`, `CompressionSpec`, `PathSpec`, `ChunkerParams`, `tag_validator`, `relative_time_marker_validator`, `timestamp`, and `parse_file_size`. It builds help choices from registered help topics and subcommand names, substitutes static choice lists into the selected shell preamble, asks `shtab` to emit the script, and prints it. Generated shell functions later run in the user's shell; dynamic archive and tag completion invoke `borg repo-list` with detected `--repo`/`-r` context.

## State and Persistence Behavior

The Python command itself only prints a completion script. The generated script has runtime side effects when used interactively: archive and tag completion spawn `borg repo-list`, read repository metadata, may require repository/passphrase environment configuration, and suppress stderr to avoid noisy completions. There is no persistent cache in this module.

## Dependencies and Integration Points

The module depends on `shtab`, Borg's custom argparse classes (`ArgumentParser`, `ActionSubCommands`), helper validator/type classes, `timestamp`, `partial_format()`, and `AI_HUMAN_SORT_KEYS`. It integrates with every command parser because it tags actions by type across the full parser tree. The shell preambles integrate with the `borg repo-list` output format contract, so changes to archive/tag formatting or command names can affect completions.

## Risks and Edge Cases

The embedded shell code must handle bash and zsh quoting, word splitting, `COMP_WORDBREAKS`, `--repo=value`, `--repo value`, `-r=value`, `-rVALUE`, and `-r VALUE` forms. Dynamic completions can be slow or fail silently for locked, encrypted, remote, or prompt-requiring repositories. Static completion lists for compression specs, chunker params, relative times, file sizes, and files-cache tokens can drift from parser validation. Recursive attachment matches by type identity, so wrapper validators or equivalent classes will not receive custom completions unless added explicitly.

## Test Signals

Tests should generate bash and zsh scripts and assert that custom functions are present, parser actions get the expected `complete` metadata, help choices include command names and help topics, sort/files-cache comma completions avoid duplicates and mutual exclusions, and archive/tag completions parse all repository option forms. Shell-level smoke tests should cover `aid:` prefixes, empty repositories, repository paths with spaces, stderr-suppressed failures, and both bash and zsh loading.
