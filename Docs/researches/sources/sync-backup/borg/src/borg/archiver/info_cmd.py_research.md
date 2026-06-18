# sources/sync-backup/borg/src/borg/archiver/info_cmd.py

## Purpose

`info_cmd.py` implements `borg info`, showing detailed information for one archive or an archive-filtered set. It formats archive metadata and stats as text or JSON. The source was read as a complete 87-line file.

## Important APIs, Types, and Functions

`InfoMixIn.do_info()` opens the repository with cache and read compatibility, resolves archive candidates, constructs `Archive` objects with the shared cache, calls `archive.info()`, formats duration and tags for text output, or accumulates raw info for JSON. `build_parser_info()` registers `--json`, archive filters, and optional archive name.

## Control Flow

The command chooses either a single archive from `manifest.archives.get_one()` or a list from `manifest.archives.list_considering(args)`. It iterates each archive, fetches `archive.info()`, prints a formatted text block with name, fingerprint, comment, host/user, tags, nominal/start/end times, duration, command line, cwd, number of files, and original size, inserting blank lines between archives. In JSON mode it prints `basic_json_data()` with an `archives` array.

## State and Persistence Behavior

The command is read-only but uses the cache because archive info can depend on cached repository/chunk metadata. It writes only stdout. It does not alter manifests, archives, repository objects, or cache contents beyond normal read/cache access side effects.

## Dependencies and Integration Points

It depends on `Archive.info()`, manifest archive filtering, `format_timedelta()`, `basic_json_data()`, and `json_print()`. Its JSON output is part of Borg's machine-readable interface and should stay compatible with scripts.

## Risks and Edge Cases

Large filtered archive sets instantiate and inspect each archive. Text mode transforms `duration` from seconds to a string and joins tags, while JSON preserves raw structures, so tests need to distinguish output modes. Missing/corrupt archives are handled by lower-level manifest/archive resolution.

## Test Signals

Tests should cover single archive and filtered multi-archive info, text formatting fields, blank-line separation, JSON archive array, tag formatting, duration conversion, and cache-required archive stats.
