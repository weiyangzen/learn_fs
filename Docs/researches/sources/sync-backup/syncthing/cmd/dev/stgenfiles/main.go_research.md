# sources/sync-backup/syncthing/cmd/dev/stgenfiles/main.go

Purpose: development utility that generates a randomized directory tree of files for sync/scanner testing.

Important APIs/types/functions: flags `-dir`, `-files`, `-maxexp`, and `-src`; functions `generateFiles`, `generateOneFile`, `randomName`, `readRand`, and `infiniteReader.Read`.

Control flow: opens a data source, then for each file generates a hex name, sometimes prefixes dotfile marker, creates nested directories based on name bytes, chooses size around a random power of two up to `maxexp`, copies from a looping source reader, chmods random permissions with owner-read forced, and sets mtime within the last 30 days.

State and persistence behavior: creates directories and files, changes permissions and timestamps. Randomness uses `math/rand` without explicit seeding, so generated sequences are deterministic across process starts unless Go runtime seeding changes.

Dependencies/integration: standard library only. Useful for Syncthing scanner/indexer stress data.

Risks/test signals: default `~/files` is not shell-expanded by Go, so it creates a literal path component if not overridden. `log.Fatal` inside helper exits on mkdir errors. Signal is a populated test tree with varied sizes, modes, mtimes, and dotfiles.
