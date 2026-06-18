# sources/sync-backup/bup/lib/bup/cmd/fsck.py

## Purpose
`fsck.py` verifies pack integrity and optionally generates or uses par2 recovery data. It distinguishes normal verification, parity generation, repair, quick checksum verification, and a `--par2-ok` capability probe.

## APIs and Control Flow
Key helpers include `par2_setup`, `is_par2_parallel`, `par2`, `par2_generate`, `par2_recovery_file_status`, `git_verify`, `attempt_repair`, `do_pack`, and `merge_exits`. `main(argv)` configures global `opt`, discovers pack stems from arguments or the repository, reports stray pack-related files, determines mode, and processes packs serially or with forked workers limited by `--jobs`. Verification uses `git verify-pack` unless `--quick` checks trailing SHA1 checksums. Repair runs `par2 repair`, then regenerates missing/bad `.idx` with `git index-pack`.

## State, Dependencies, Integration, Risks, Tests
The command reads and may create/delete `.par2`, `.vol*.par2`, `.idx`, and temporary files near packs. It depends on external `par2` and `git`, pack naming conventions, `Sha1`, and bup exit constants where `EXIT_FALSE` can mean repair was needed or recovery info already existed. Risks include destructive repair mode, parity files left by interrupted tools, forked child error propagation, handling of missing pack/index files, and old par2 implementations lacking `-t1`. Test signals include parity status classification, quick checksum failures, generation tempdir cleanup, repair paths that rebuild indexes, parallel job exit merging, and `--par2-ok` incompatibility checks.
