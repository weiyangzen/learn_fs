
# sources/sync-backup/restic/internal/repository/packer_manager.go

Purpose: manages open packers for blob writes, temporary pack files, random blob distribution across packers, flush-time pack merging, and final pack upload/index update.

Important types are local `packer` and `packerManager`. APIs include `newPackerManager`, `SaveBlob`, `Flush`, `mergePackers`, `pickPacker`, `newPacker`, `forgetPacker`, and `Repository.savePacker`. `SaveBlob` selects a packer, adds ciphertext, queues full/header-full packers, and reports storage size. `pickPacker` places oversized blobs in dedicated packs and otherwise randomly selects one of several open packers to reduce chunk-boundary leakage. `mergePackers` merges small pending packers during flush to reduce size leakage for small files.

State is persisted through temp files first, then `savePacker` finalizes the pack, hashes the pack bytes, saves it as `PackFile`, closes the temp file, and stores blob entries in the master index. Risks include lock contention, temp file cleanup on errors, random selection errors, pack merging correctness, and index/backend consistency after upload. Tests and benchmarks in `packer_manager_test.go` validate accounting and oversize behavior.
