# sources/sync-backup/borg/src/borg/archiver/transfer_cmd.py

Purpose: implements archive transfer from another repository into the current repository, optionally upgrading Borg 1.x data, recompressing file chunks, or rechunking with new chunker parameters.

Important APIs: `transfer_chunks(...)` copies or rechunks chunk lists and returns `(chunks, transfer_size, present_size)`. Direct mode checks the destination cache, fetches missing chunks from the source, handles missing source chunks by preserving `ChunkListEntry`, and either preserves compressed payloads (`recompress="never"`) or parses/recompresses (`"always"`). Rechunk mode streams source chunks through `DownloadPipeline`, wraps them in `ChunkIteratorFileWrapper`, chunks via `get_chunker`, hashes with `cached_hash`, and writes new chunks through `cache.add_chunk`. `TransferMixIn.do_transfer(...)` validates key/chunker compatibility, selects archives, validates names/comments, selects an upgrader, skips already-present archives, transfers each item, upgrades metadata, and saves the new archive.

Control flow and state: the command is decorated with `with_other_repository(...READ...)` and `with_repository(...WRITE..., cache=True)`. It writes destination chunks through cache/repository APIs, updates archive stats, creates destination archives only when not in dry-run mode, and uses name/timestamp or name/id checks to avoid duplicate transfers. Borg 1.x checkpoint part files are skipped.

Dependencies and integration: integrates source and destination manifests, `Archive`, `DownloadPipeline`, cache chunk index behavior, `crypto.key.uses_same_id_hash`, `uses_same_chunker_secret`, legacy repository exceptions, upgrade modules, validators, and archive filter definitions.

Risks: without rechunking, the source and destination must use compatible ID hashing and the same chunker secret; the command raises early because otherwise deduplication or chunk IDs would be invalid. Missing chunks in the source are intentionally represented rather than replaced with zero data, which preserves metadata but leaves later reads dependent on repair/reappearance behavior. The dry-run rechunk path estimates size without populating chunk entries, so it should not be treated as a full validation of write behavior.

Test signals: exercise same-key transfers, incompatible key errors, rechunk transfers across ID-hash changes, recompress never/always, Borg 1.x upgrader requirements, invalid archive names/comments, duplicate archive skipping, missing source chunk preservation, dry-run output, and filtering subsets of archives.
