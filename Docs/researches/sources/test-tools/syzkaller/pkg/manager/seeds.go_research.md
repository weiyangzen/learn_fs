# sources/test-tools/syzkaller/pkg/manager/seeds.go

Purpose: Loads and prepares initial fuzzing candidates from the corpus database and built-in syzkaller seed programs, parses seed requirements, filters disabled syscalls, and periodically marks subsets for re-minimization/re-smashing.

Important APIs and types: `Seeds` returns `CorpusDB`, `Fresh`, and `Candidates`. `LoadSeeds` is the main entry. `readInputs` reads DB records and `sys/<targetOS>/test` seed files concurrently. `CurrentDBVersion` and `versionToFlags` define corpus flag migration. `ParseSeed`, `ParseSeedWithRequirements`, `parseRequires`, `checkArch`, `MatchRequirements`, and `parseProg` handle seed parsing. `FilteredCandidates`, `FilterCandidates`, `ReminimizeSubset`, and `ResmashSubset` post-process candidates.

Control flow: `LoadSeeds` opens `corpus.db`, starts worker goroutines based on `GOMAXPROCS`, parses DB and seed inputs, classifies broken/skipped inputs, deduplicates seeds already in corpus by hash, deletes broken DB entries when mutable, flushes DB, discards record data to save memory, and returns candidates. `parseProg` checks requirements before strict/non-strict deserialization, rejects too-long programs and any call with `fail_nth`. `FilterCandidates` removes disabled calls in place and optionally clears minimization for changed corpus programs.

State and persistence: Reads and mutates `corpus.db`; deletes broken corpus records only when `immutable` is false. Candidate flags encode whether programs came from corpus, were minimized, or were smashed.

Dependencies and integration: Used by normal and diff managers to seed fuzzers. Depends on `db`, `fuzzer`, `hash`, `mgrconfig`, `osutil`, and `prog`.

Risks: Requirement parsing is comment/text based. Filtering mutates program objects in place. Random subset resets are nondeterministic by design. Skipped seeds are not errors, while broken corpus entries can be deleted.

Test signals: `seeds_test.go` covers requirement architecture handling; broader behavior is covered through manager/fuzzer integration.
