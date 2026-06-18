# sources/sync-backup/borg/src/borg/archiver/diff_cmd.py

## Purpose

`diff_cmd.py` implements `borg diff`, comparing contents and metadata between two archives. It formats text or JSON Lines output, supports content-only mode, validates and applies sort specifications, and warns when chunker parameters may force slower comparison. The source was read as a complete 338-line file.

## Important APIs, Types, and Functions

`DiffMixIn.do_diff()` is the command entry point. Local helpers `actual_change()`, `print_json_output()`, `print_text_output()`, and `key_for()` filter no-op changes, serialize `ItemDiff` changes, and compute sort keys. It uses `Archive.compare_archives_iter()` for comparison and `DiffFormatter` for text formatting. `build_parser_diff()` defines flags such as `--numeric-ids`, `--same-chunker-params`, `--format`, `--json-lines`, `--sort-by`, `--content-only`, two archive names, paths, and exclusions. `diff_sort_spec_validator()` restricts accepted sort fields.

## Control Flow

The command resolves both archive names from the manifest and constructs `Archive` instances. It compares archive chunker parameters; if they differ and the user has not asserted sameness, it warns and disables chunk-ID-only comparison. It builds a matcher from patterns and path arguments, calls `Archive.compare_archives_iter()`, filters equal items, optionally materializes and stably sorts the result list from last sort key to first, then emits each diff as JSON Lines or formatted text. Finally it warns for unmatched include patterns.

## State and Persistence Behavior

The command is read-only with repository read compatibility. It may load archive metadata and content chunks depending on comparison mode and chunker compatibility, but it does not mutate repository, cache, or manifest state. Output is written to stdout and warnings to Borg's warning channel.

## Dependencies and Integration Points

The module depends on `Archive`, `ItemDiff`, `DiffFormatter`, `BaseFormatter`, `BorgJsonEncoder`, path pattern helpers from `_common`, and archive-name/path validators. Its performance depends on archive metadata including `chunker_params`, and its output contract integrates with scripts using `BORG_DIFF_FORMAT` or `--json-lines`.

## Risks and Edge Cases

When chunker params differ, modified-file change objects may not contain `added` and `removed`; `actual_change()` treats that conservatively as a real change. Sorting forces the generator into memory, which can be expensive on huge archives. `content_only` filters metadata fields by comparing change names to `DiffFormatter.METADATA`. Sort keys read private-ish fields (`_item1`, `_item2`) from `ItemDiff`, so formatter/data structure changes can break sorting.

## Test Signals

Tests should compare archives with added, removed, modified, metadata-only, and unchanged items; verify content-only filtering; assert JSON Lines schema; exercise chunker mismatch warnings and `--same-chunker-params`; cover each sort field and direction; validate bad sort specs; test custom formats and `BORG_DIFF_FORMAT`; and confirm unmatched include warnings.
