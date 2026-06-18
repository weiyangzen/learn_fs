# sources/sync-backup/borg/src/borg/archiver/list_cmd.py

## Purpose

`list_cmd.py` implements `borg list`, listing items contained in an archive with configurable text or JSON Lines formatting and optional path/depth filtering. The source was read as a complete 133-line file.

## Important APIs, Types, and Functions

`ListMixIn.do_list()` resolves the archive, builds a matcher, chooses a format from `--format`, `--short`, or `BORG_LIST_FORMAT`, constructs an `ItemFormatter`, and iterates archive items. `ItemFormatter.format_needs_cache()` decides whether to open `Cache`. `build_parser_list()` registers `--short`, `--format`, `--json-lines`, `--depth`, archive name, paths, and exclusions.

## Control Flow

The command builds a path/pattern matcher, selects a format string, resolves the target archive, and defines `_list_inner(cache)`. Inside it, an `Archive` is opened with optional cache and an `item_filter()` checks matcher results and maximum slash-count depth. It then writes each formatted item to stdout. Cache acquisition is deferred and avoided unless the selected format needs cache-derived fields.

## State and Persistence Behavior

The command is read-only and writes listing output to stdout. It may open the cache for read access or cache population if the formatter requires it, but no archive or manifest mutation is intended.

## Dependencies and Integration Points

Dependencies include `Archive`, `Cache`, `ItemFormatter`, `BaseFormatter` help text, matcher/exclusion helpers, and environment-variable format overrides. It shares path filtering semantics with extract/diff and formatter infrastructure with repo-list/prune.

## Risks and Edge Cases

Depth is computed by counting `/`, so root-level files have depth 0 and nested paths depend on archive path normalization. JSON Lines ignores the display form of `--format` but uses keys referenced in it, which can surprise callers. Cache opening is format-dependent, so adding formatter keys must keep `format_needs_cache()` accurate.

## Test Signals

Tests should list archives in default, short, custom format, and JSON Lines modes; verify path and exclusion filtering; verify depth boundaries; cover cache-needed and cache-free formats; validate `BORG_LIST_FORMAT`; and assert formatter help includes the advertised keys.
