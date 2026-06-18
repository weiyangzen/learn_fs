# sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/InMemoryFile.cpp

Purpose: implements simple byte-buffer backed file objects for tests.

Important APIs/functions: `InMemoryFile::read()` copies a bounded slice from `_data`; `data()`, `size()`, and `fileContentEquals()` expose raw content checks. `WriteableInMemoryFile::write()` extends then overwrites; `sizeUnchanged()` and `regionUnchanged()` compare against original data.

Control flow: reads compute `min(count, data_size - offset)` and copy from `dataOffset()`. Writes call `_extendFileSizeIfNecessary(count + offset)`, allocate a new `Data` object if needed, copy old bytes, then write the caller buffer.

State/persistence: all state is process memory. `WriteableInMemoryFile` snapshots `_originalData` at construction for later assertions. There is no disk persistence.

Dependencies/integration: uses `cpputils::Data`, `fspp::num_bytes_t`, `std::memcpy`, and `std::memcmp`.

Risks: callers must provide valid offsets; subtracting an offset beyond size could underflow depending on `num_bytes_t` behavior. `_extendFileSize()` does not explicitly zero-fill new space beyond whatever `Data(size)` initializes.

Test signals: these helpers support tests that verify read/write offsets, growth, and unchanged regions without touching real files.
