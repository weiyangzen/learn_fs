# sources/sync-backup/bup/lib/bup/cmd/index.py

## Purpose
`index.py` maintains the filesystem index consumed by `bup save`. It updates, prints, checks, clears, and reports modified entries while storing compact metadata and hardlink information.

## APIs and Control Flow
`IterHelper` tracks the current old-index entry. `check_index` validates reader iteration invariants. `clear_index` removes stat/meta/hlink index files. `update_index` traverses paths with `recursive_dirlist`, compares new stat data against old entries, marks deleted paths, updates metadata through `MetaStoreWriter`, maintains `HLinkDB`, optionally fakes hash validity, and merges old/new index writers. `main(argv)` applies mode defaults, sleeps to avoid timestamp races, parses excludes, reduces paths, and handles update/print/status/modified/check flows.

## State, Dependencies, Integration, Risks, Tests
Persistent state is the bup index triple: stat index, metadata store, and hardlink database. Dependencies include `metadata.from_path`, `index.Reader/Writer`, `hlinkdb`, `recursive_dirlist`, exclude parsing, and default index path helpers. It directly feeds `save.py`, which trusts valid SHA and metadata offsets. Risks include timestamp race comments, device-change invalidation, deleted entries retained until merge policy changes, hardlink DB consistency, and fake-valid/invalid misuse. Test signals include stale detection, mode/status output, excludes/xdev behavior, metadata time clearing, merge with existing index, check-mode invariants, and `--clear` restrictions.
