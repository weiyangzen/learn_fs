# sources/sync-backup/bup/lib/bup/cmd/rm.py

## Purpose
`rm.py` removes branches or saves from a bup repository through the shared `bup.rm.bup_rm` implementation. It is an experimental destructive command guarded by `--unsafe`.

## APIs and Control Flow
`main(argv)` parses compression, verbosity, `--unsafe`, and one or more target paths. It refuses to run without `--unsafe`, requires at least one path, checks that the repository exists, opens `LocalRepo`, converts targets to bytes, and calls `bup_rm(repo, targets, compression=..., verbosity=...)`.

## State, Dependencies, Integration, Risks, Tests
Persistent effects are delegated to `bup_rm`, likely including ref updates and new pack/object state for rewritten reachable history. Dependencies are `Options`, `check_repo_or_die`, `LocalRepo`, and `argv_bytes`. Risks are destructive target interpretation, no pretend mode here, and compression defaults influencing rewritten objects. Test signals include unsafe gate, target requirement, compression/verbosity forwarding, byte path conversion, and repository-open lifetime around `bup_rm`.
