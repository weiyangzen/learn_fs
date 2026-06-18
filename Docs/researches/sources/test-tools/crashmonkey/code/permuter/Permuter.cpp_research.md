# sources/test-tools/crashmonkey/code/permuter/Permuter.cpp

Purpose: implements common permutation machinery for converting a logged bio stream into persistence epochs and generating de-duplicated crash states.

Important APIs/functions: `BioVectorHash` and `BioVectorEqual` hash/check generated crash-state identities. `epoch_op::ToSectors()` splits a bio into sector-sized pieces. `epoch_op::ToWriteData()` and `EpochOpSector::ToWriteData()` produce replayable `DiskWriteData`. `Permuter::InitDataVector()` groups `disk_write` entries into epochs using barriers and checkpoints. `GenerateCrashState()` and `GenerateSectorCrashState()` invoke subclass generators and reject duplicate states. `CoalesceSectors()` keeps only the latest sector write for each disk offset.

Control flow: `InitDataVector()` scans the logged data, starts epochs, handles checkpoint entries by updating checkpoint epoch numbers, records overlap metadata, and splits flush-with-data operations into a zero-size flush half and a data half for the next epoch unless FUA is present. Generation calls the subclass for a candidate, builds a uniqueness vector from bio indices or sector indices, retries until unique or the retry heuristic expires, then fills result vectors and `PermuteTestResult`.

State and persistence behavior: the object stores `epochs_`, selected `sector_size_`, and an in-memory set of completed permutations. It does not persist choices; repeatability depends on subclass RNG.

Dependencies and integration: consumes `utils::disk_write` from the wrapper log and produces `utils::DiskWriteData` for `Tester::test_write_data()`. Subclasses such as `RandomPermuter` implement the abstract generation hooks.

Risks: overlap range math mixes sectors and byte sizes (`metadata.size`) and may mark ranges inaccurately unless sizes are in sectors. `epoch::num_meta` is incremented without visible initialization when `epochs_.emplace_back()` value-initializes a POD-like struct; this may be undefined if not zeroed. Duplicate detection stores only operation indexes, not data content. Retry cutoff is heuristic and can stop before exhausting state space.

Test signals: useful tests feed artificial logs with checkpoints, flush/FUA/data combinations, overlapping writes, and duplicate states, then verify epoch boundaries and generated replay vectors.
