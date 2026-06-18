# sources/sync-backup/borg/src/borg/archiver/repo_space_cmd.py

## Purpose

`repo_space_cmd.py` implements `borg repo-space`, managing emergency reserved space inside a repository so users can recover from disk-full situations by freeing preallocated reserve objects. The source was read as a complete 106-line file.

## Important APIs, Types, and Functions

`RepoSpaceMixIn.do_repo_space()` opens the repository without lock or manifest, then either reserves space, frees reserve objects, or reports current reserve size. It uses 64 MiB `space-reserve.N` objects under the repository `config` namespace, `os.urandom()` to resist compression/deduplication, `repository.store_store()`, `repository.store_list()`, and `repository.store_delete()`. `build_parser_repo_space()` registers `--reserve SPACE` parsed by `parse_file_size` and `--free`.

## Control Flow

When `--reserve` is positive, the command rounds requested bytes up to 64 MiB objects, writes random data to `config/space-reserve.0`, `.1`, and so on, sums written bytes, and prints the reserved amount. When `--free` is set, it lists `config`, wraps RPC tuples as `ItemInfo`, deletes objects whose names start with `space-reserve.`, sums sizes, and prints follow-up instructions. With neither option, it lists existing reserve objects and reports total reserved space plus how to change it.

## State and Persistence Behavior

The command intentionally works without locks because lock acquisition may fail when the disk is full. Reserving writes large random config objects to persistent repository storage. Freeing deletes those config objects. Reporting is read-only. Existing reserve objects are overwritten/reused by deterministic names when reserving again without freeing first.

## Dependencies and Integration Points

It depends on borgstore `ItemInfo`, repository config store APIs, file-size parsing/formatting, and parser helper `Highlander`. It is referenced by `repo_create_cmd.py` guidance and operationally supports later `prune`, `delete`, and `compact` recovery.

## Risks and Edge Cases

Working without locks is deliberate but means concurrent reserve/free operations can race. Random reserve data consumes CPU and memory in 64 MiB chunks. Re-reserving without `--free` can overwrite or add deterministic reserve names depending on store semantics. Prefix matching deletes any config item starting `space-reserve.`, so unrelated objects should not use that prefix.

## Test Signals

Tests should cover reserve rounding, zero/default report, free deleting only matching config objects, RPC tuple conversion through `ItemInfo`, parse-file-size inputs, formatting output, no-lock repository opening, and concurrent/race behavior in integration tests where possible.
