# sources/sync-backup/borg/src/borg/archiver/_common.py

## Purpose
`_common.py` contains shared archiver infrastructure: repository-opening decorators, archive-loading wrappers, parser help processing, common option registration, include/exclude pattern options, archive filter options, and matcher/filter construction. It is the main integration layer between command methods and repository/manifest/cache lifecycles.

## Important APIs, Types, and Functions
- `get_repository(location, create, exclusive, lock_wait, lock, args, v1_legacy)` selects `Repository`, legacy repository, legacy remote repository, or direct BorgStore-backed protocols based on location protocol and Borg 1 compatibility.
- `compat_check(...)` validates decorator arguments and derives manifest compatibility checks for create operations.
- `with_repository(...)` decorates command methods, opens the primary repository, checks repository version, loads manifest/repo object adapter, optionally asserts security, opens cache, and passes `repository`, `manifest`, and/or `cache`.
- `with_other_repository(...)` mirrors that behavior for `--other-repo` source repositories used by transfer-like commands.
- `with_archive(method)` resolves `args.name` to an archive id and injects an `Archive` instance configured from CLI flags.
- `process_epilog(epilog)` dedents RST help, removes man-only lines for command-line/build usage, and converts references for terminal display.
- `define_exclude_and_patterns`, `define_exclusion_group`, and `define_archive_filters_group` register shared argparse options for path patterns and archive selection.
- `define_common_options(add_common_option)` registers global options such as logging, progress, lock wait, repository location, remote path, upload throttling, profiling, and shell command.
- `build_matcher` and `build_filter` create pattern matchers and item filters for include/exclude and strip-components behavior.

## Control Flow
Decorator factories validate compatibility arguments at definition time and return wrappers. At command invocation, `with_repository` validates that a repository location is present, computes lock behavior, opens the repository context, checks supported repository version, loads a `Manifest` with `RepoObj` or legacy `RepoObj1` when needed, applies compression overrides, asserts secure cache/repository state, optionally opens `Cache`, and then calls the command. `with_other_repository` follows the same flow for secondary source repositories but returns without opening one when the other location is absent. Parser helper functions are invoked during `Archiver.build_parser()` and produce consistent option groups across commands.

## State and Persistence Behavior
The wrappers acquire repository locks, open/close repository and cache contexts, may create repositories when requested, and may initialize or validate local cache state. They do not themselves write archive content, but create/exclusive/cache options determine whether downstream commands can mutate repository state. Parser helpers create argparse state only. Matchers are in-memory structures derived from CLI patterns and paths.

## Dependencies and Integration Points
The module depends on `borg` package doc-mode metadata, `Archive`, constants, `Cache`, `assert_secure`, helper validators/types (`Location`, `SortBySpec`, `Highlander`, `PositiveInt`, etc.), RST terminal conversion, `Manifest`, `PatternMatcher`, repository classes, repo object adapters, and argparse pattern actions. It is imported by command mixins throughout `src/borg/archiver/` and by the top-level `Archiver`.

## Risks and Edge Cases
- Repository protocol/version selection is security-sensitive, especially legacy `ssh://` support and direct BorgStore protocols.
- Compatibility checks are enforced by decorator configuration; a command using the wrong compatibility tuple can allow unsupported manifest feature access.
- `with_archive` assumes `args.name` exists and resolves exactly one archive through the manifest.
- Common option defaults depend on being registered once with defaults and again under subparsers with `SUPPRESS`; mistakes can change precedence.
- `build_filter` strip-components matching compares `os.sep`-split path components; archive paths are generally POSIX-like, so platform path separator assumptions should be considered.

## Test Signals
Tests should exercise decorated commands with file/rest/sftp/cloud protocols, legacy Borg 1 allowed/disallowed paths, missing repository location, repository version mismatch, manifest compatibility errors, cache opening modes, secure cache assertions, other-repository handling, and archive resolution. Parser tests should validate common option precedence, archive filter mutual exclusions, pattern-file actions, strip-components filters, and terminal/RST help rendering.
