# sources/sync-backup/bup/lib/bup/cmd/gc.py

## Purpose
`cmd/gc.py` is the CLI wrapper for bup garbage collection. It guards an experimental destructive operation behind `--unsafe` and forwards validated options to `bup.gc.bup_gc`.

## APIs and Control Flow
`main(argv)` parses verbosity, garbage threshold, compression, `--ignore-missing`, and `--unsafe`. It rejects positional arguments, requires `--unsafe`, validates `threshold` as an integer percentage from 0 to 100, checks that a repository exists, then invokes `bup_gc(threshold=..., compression=..., verbosity=..., ignore_missing=...)`.

## State, Dependencies, Integration, Risks, Tests
The wrapper itself persists nothing, but it triggers pack rewrites, bloom/midx clearing, reflog expiration, and object deletion in `bup.gc`. It depends on `git.check_repo_or_die`, option parsing, and the library GC implementation. Risks are mostly delegated: interrupted GC can leave derived indexes cleared and requires rerunning before adding data. Test signals include `--unsafe` refusal, threshold validation, no positional args, forwarding of compression/verbosity/ignore-missing, and repository requirement.
