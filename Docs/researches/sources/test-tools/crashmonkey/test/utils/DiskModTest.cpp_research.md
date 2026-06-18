# sources/test-tools/crashmonkey/test/utils/DiskModTest.cpp

Purpose: gtest/gmock suite for `DiskMod` serialization and deserialization. It validates binary sizes, endian-converted headers, enum fields, paths, range metadata, and optional payload bytes for major mod types and options.

Important APIs/types/functions: `DiskMod::Serialize`, `DiskMod::Deserialize`, `be16toh`, `be64toh`, `shared_ptr<char>`, parameterized path tests, option tests, fallocate option/type combinations, and gtest assertions.

Control flow: individual tests build a `DiskMod`, serialize it, manually inspect size/type/option fields, deserialize into a new object, and assert all relevant fields. Parameterized tests cover short and long paths, all `ModOpts`, and both data/data-metadata fallocate-style mods.

State/persistence behavior: all state is in-memory serialized buffers; no files are written. Dependencies/integration: protects the binary contract consumed by wrapper serialization and replay tools.

Risks/test signals: malformed input, remove mods, directory data mods, and `SerializeDirectoryMod` are not covered. The tests encode current size formulas, so intentional format changes require synchronized updates.
