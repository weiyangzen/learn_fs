# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcIOFileBlock.cc

## Purpose
Implements the older block-file cache mode where one logical remote object is split across multiple local `File` objects, each representing an HDFS-style block. It maintains a top-level `.cinfo` for logical file size and lazily creates block files as read ranges touch them.

## Important APIs, Types, and Functions
- Constructor initializes `m_blocksize` from configuration or `hdfsbsize=` URL parameter and calls `initLocalStat()`.
- `initLocalStat()` reads an existing top-level `.cinfo` for file size or queries upstream `Fstat` and writes a new top-level `.cinfo`.
- `newBlockFile()` builds names of the form `<origpath>___<blocksize>_<offset>` and asks `Cache::GetFile` for a `File`.
- `Read()` splits the user range across logical blocks, gets/creates each block `File`, performs synchronous block reads, and falls back to upstream direct reads if block file creation failed.
- `Update()`, `ioActive()`, and `DetachFinalize()` iterate over all block `File` objects.
- `CloseInfoFile()` writes top-level access stats and closes the logical `.cinfo`.

## Control Flow
Read flow clamps to logical file size, computes first/last block, obtains the per-block `File` under `m_mutex`, adjusts per-block read size for edge blocks, performs a synchronous `File::Read` using an internal condition handler, then advances the output buffer and logical offset. A partial non-error block read is treated as `-EIO`; a negative read result is propagated.

## State and Persistence Behavior
Persistent state includes the top-level `.cinfo` for logical file size and per-block data/metadata files named with size/offset suffixes. Runtime state includes `m_blocks`, `m_localStat`, `m_info`, and `m_info_file`. Per-block persistence is delegated to each `File`.

## Dependencies and Integration Points
Depends on `Cache`, `File`, `Info`, `Stats`, `XrdOss`, `XrdSfs`, `XrdOucEnv`, and trace macros. It integrates with the same `File`/`Cache` machinery as whole-file mode but adds a map of block `File` references.

## Risks and Test Signals
Risks include non-obvious offset semantics when calling `fb->Read(this, buff, off, readBlockSize, ...)`, storing null `File*` in the block map after local open failure, memory ownership of `m_localStat`, and top-level `.cinfo` consistency versus per-block files. Tests should read ranges spanning first/middle/last blocks, simulate failed block-file open fallback, check detach releases every block, and restart from top-level `.cinfo`.
