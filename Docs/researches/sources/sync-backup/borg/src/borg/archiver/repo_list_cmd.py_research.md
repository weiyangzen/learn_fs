# sources/sync-backup/borg/src/borg/archiver/repo_list_cmd.py

## Purpose

`repo_list_cmd.py` implements `borg repo-list`, listing archives contained in a repository in text or JSON form, with archive filtering and optional deleted archive visibility. The source was read as a complete 110-line file.

## Important APIs, Types, and Functions

`RepoListMixIn.do_repo_list()` selects a format from `--format`, `--short`, or `BORG_REPO_LIST_FORMAT`, constructs `ArchiveFormatter`, iterates `manifest.archives.list_considering(args)`, writes formatted rows or accumulates JSON data, and emits `basic_json_data()`. `build_parser_repo_list()` registers `--short`, `--from-borg1`, `--format`, `--json`, and archive filters with deleted support.

## Control Flow

The command opens a repository for read and allows Borg 1 repositories. It chooses the format, passing `deleted=args.deleted` to the formatter. It iterates archive infos selected by archive filters, writing text rows to stdout or collecting formatter item data. JSON mode prints a top-level Borg JSON structure with `archives`.

## State and Persistence Behavior

The command is read-only and writes stdout. It may read deleted archive entries when requested through filter options. It does not require cache.

## Dependencies and Integration Points

Dependencies include `ArchiveFormatter`, `BaseFormatter` help text, archive filter helper definitions, `basic_json_data()`, and environment format override support. `completion_cmd.py` shell snippets call `borg repo-list` with custom formats to complete archive names, IDs, and tags, making this output functionality an integration point for shell completions.

## Risks and Edge Cases

`--short` outputs IDs rather than archive names, which differs from some list commands. JSON ignores display formatting except for included keys as implemented by formatter. Deleted archive handling must stay consistent with soft-delete behavior from delete/prune and final removal by compact.

## Test Signals

Tests should cover default, short, custom format, environment format, JSON, archive filters, deleted archive listing, Borg 1 compatibility flag parsing, and formatter key help text. Completion integration should verify formats like `{id}{NL}`, `{archive}{NL}`, and `{tags}{NL}` remain valid.
