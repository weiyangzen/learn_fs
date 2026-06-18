# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_cp.py

## Purpose
Implements `tahoe cp`, including local-to-grid, grid-to-local, grid-to-grid, file-cap-to-file, and recursive directory copying. It abstracts sources and targets as local/Tahoe file/directory/missing objects so `Copier.try_copy()` can enforce cp-like semantics before dispatching to byte copy, URI link, directory creation, and child-link updates.

## Important APIs, Types, and Functions
Key exceptions are `MissingSourceError`, `FilenameWithTrailingSlashError`, and `WeirdSourceError`. HTTP helpers `GET_to_file`, `GET_to_string`, `PUT`, `POST`, `mkdir`, and `make_tahoe_subdirectory` wrap `common_http.do_http` with Tahoe webapi status checks. Source/target classes include `LocalFileSource`, `LocalDirectorySource`, `TahoeFileSource`, `TahoeDirectorySource`, `LocalFileTarget`, `LocalDirectoryTarget`, `TahoeFileTarget`, `TahoeDirectoryTarget`, and missing-target variants. `Copier.do_copy()` is the command entry point, `get_source_info()` and `get_target_info()` classify operands, `copy_file_to_file()` handles single-file output, and `copy_things_to_directory()` handles recursive/directory cases.

## Control Flow
`copy(options)` instantiates `Copier` and calls `do_copy()`. `try_copy()` normalizes the node URL, resolves aliases first for the destination and then each source, determines whether the destination is a file or directory, validates recursive and multi-source constraints, and then either copies one file or builds a target map. Directory copies populate sources recursively, lazily populate target children, create missing local/Tahoe directories, detect same-name collisions in each target directory, then walk the target map copying files and calling `set_children()` for Tahoe directories.

## State and Persistence Behavior
Local output is persisted with `fileutil.put_file()` or `os.makedirs()`. Tahoe uploads go through webapi `PUT /uri` or `PUT /uri/<cap>/<path>`, while directory link mutations are batched in `TahoeDirectoryTarget.new_children` until `set_children()` posts `?t=set_children`. Tahoe directory/source objects cache parsed child JSON by read/write capability in `Copier.cache`, limiting duplicate directory fetches during recursive copies. Immutable Tahoe-to-Tahoe file copies can avoid byte transfer by linking the source cap; mutable files and local targets force byte copies.

## Dependencies and Integration Points
Depends on `allmydata.scripts.common` for alias parsing and path escaping, `common_http` for webapi calls, `allmydata.uri` for readonly caps after mkdir, `encodingutil` for terminal/path conversions, and `jsonbytes` for directory JSON. Integrates with Tahoe webapi endpoints `GET ?t=json`, `POST ?t=mkdir`, `PUT ?t=uri`, and `POST ?t=set_children`.

## Risks and Edge Cases
`need_to_copy_bytes()` checks `source.need_to_copy_bytes` rather than calling it, matching an in-file FIXME and preserving bug-compatible behavior. URI-link copying has TODOs around forward compatibility and mutable handling. Local special files are rejected or skipped; dangling symlinks under recursive local dirs are ignored. The module relies on webapi JSON shapes and may fail hard on unknown node types.

## Test Signals
`src/allmydata/test/cli/test_cp.py` covers Unicode filenames/directories, dangling symlinks, raw filecaps, missing aliases, recursive copy behavior, collision and directory/file overwrite cases, verbose progress, and grid/local round trips. Broader CLI help/import tests in `test_cli.py` also exercise command registration.
