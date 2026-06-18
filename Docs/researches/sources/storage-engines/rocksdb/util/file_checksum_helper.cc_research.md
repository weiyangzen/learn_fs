# sources/storage-engines/rocksdb/util/file_checksum_helper.cc

Purpose: implementation of default file checksum list storage and checksum generator factory registration/loading.

Important APIs/functions: `FileChecksumListImpl::{reset,size,GetAllFileChecksums,SearchOneFileChecksum,InsertOneFileChecksum,RemoveOneFileChecksum}` manage an in-memory map. `NewFileChecksumList()` returns a new implementation. `GetFileChecksumGenCrc32cFactory()` returns a static shared default factory. `FileChecksumGenFactory::CreateFromString()` registers built-ins once and loads either the default CRC32C factory or a shared-object factory.

Control flow: list methods validate output pointers where relevant, use unordered_map lookup/insert/erase, and return `Status::NotFound()` for missing files. Factory creation uses `std::call_once()` to register `FileChecksumGenCrc32cFactory` in `ObjectLibrary`.

State and persistence: `FileChecksumListImpl` keeps in-memory file-number to checksum/name pairs. `GetFileChecksumGenCrc32cFactory()` and factory registration use process-static state. Actual checksum bytes are persisted by callers.

Dependencies and integration: depends on `file_checksum_helper.h`, `customizable_util.h`, `ObjectLibrary`, and `LoadSharedObject`. Integrated with options/config parsing and SST file checksum generation.

Risks: `GetAllFileChecksums()` iteration order is unordered. Pointer validation prevents null writes but insert accepts any checksum/name content. Shared object loading can fail based on config/environment.

Test signals: no direct test in this subset; `file_reader_writer_test.cc` exercises checksum handoff at writer level.
