# sources/test-tools/crashmonkey/test/utils/DiskWriteTest.cpp

Purpose: gtests for block-level `disk_write` serialization/deserialization. It verifies that metadata flags, sector, size, and payload survive round-trip through temporary files.

Important APIs/types/functions: `disk_write`, `set_data`, `get_data`, `serialize`, `deserialize`, `mkstemp`, `ofstream`, `ifstream`, `memcmp`, `REQ_WRITE`, and `REQ_SYNC`.

Control flow: `Serialize_Deserialize` writes one 8 KiB record to a temp file and reads it back. `Serialize_Deserialize_Epoch` writes two records with different sizes/data bytes, reads until EOF, and compares each record field and payload.

State/persistence behavior: writes temporary serialized log files under `/tmp` and frees temp path strings, but does not unlink the files. Dependencies/integration: validates utility format used by disk log processing and permuters.

Risks/test signals: file streams are not explicitly binary, tests depend on Linux block headers, and the EOF loop can be fragile because serialized records are block padded. There is debug output in the epoch test.
