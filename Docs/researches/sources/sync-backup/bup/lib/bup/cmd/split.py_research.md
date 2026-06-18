# sources/sync-backup/bup/lib/bup/cmd/split.py

## Purpose
`split.py` chunks input data with bup's rolling hashsplit algorithm and writes blobs, trees, commits, named saves, copied input, or no-op benchmark output.

## APIs and Control Flow
`opts_from_cmdline` validates mutually exclusive modes, git-id input, pack sizing, fanout, bandwidth, date, remote repo, `BUP_SERVER_REVERSE` stdin restrictions, and save names. `split` applies progress callbacks, then chooses `split_to_blobs`, `split_to_blob_or_tree`, `split_to_shalist`, or raw hashsplit iteration depending on mode. It prints blob/tree/commit IDs as requested and creates commit messages with trailers. `main` configures hashsplit fanout and client bandwidth, opens stdin/files or git object iterators, conditionally opens/creates a repository, loads split config, writes objects or calculates null hashes, and updates a named ref after writing.

## State, Dependencies, Integration, Risks, Tests
Persistent effects are blobs/trees/commits and optional branch ref updates; `--copy` and `--noop` avoid repository writes. Dependencies include `hashsplit`, repo location helpers, `git.CatPipe`, packwriter options, commit helpers, and config parsing. Risks include option interaction bugs, `--max-pack-objects` assigning to `max_pack_size` in code, stdin restrictions under reverse server mode, ref update after writes, and benchmark division by zero for instant runs. Test signals include all mode combinations, git-id streaming, keep-boundaries, no-repo copy/noop behavior, named save dummy tree entry, remote writes, and compression/pack limits.
