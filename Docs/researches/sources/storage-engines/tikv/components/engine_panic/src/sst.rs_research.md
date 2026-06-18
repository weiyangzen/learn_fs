# sources/storage-engines/tikv/components/engine_panic/src/sst.rs

Purpose: Panic skeleton for SST reading, writing, builder configuration, external SST metadata, and streaming readers.

Important APIs and types: `PanicEngine` implements `SstExt` with `PanicSstReader`, `PanicSstWriter`, and `PanicSstWriterBuilder`. Reader implements checksum and kv-count APIs plus `RefIterable`; writer implements put/delete/size/finish; builder configures DB, CF, memory mode, compression, and path. `PanicExternalSstFileInfo` and `PanicExternalSstFileReader` implement external-file traits and `Read`.

Control flow and state: Every operational method panics. The iterator contains only phantom lifetime state.

Dependencies and integration: Imports `encryption::DataKeyManager`, showing real SST readers may be encryption-aware. Also tracks compression and CF-name APIs from `engine_traits`.

Risks: Runtime use panics. The broad surface is important for compile-time detection of SST trait changes.

Test signals: No tests.
