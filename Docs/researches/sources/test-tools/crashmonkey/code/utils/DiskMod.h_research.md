# sources/test-tools/crashmonkey/code/utils/DiskMod.h

Purpose: declares the `DiskMod` data model for logical filesystem changes recorded by user-tool wrappers. It is the schema for create, data, metadata, remove, sync, checkpoint, fallocate, mmap, and sync-file-range operations.

Important APIs/types/functions: class `DiskMod`, static `Serialize`/`Deserialize`, enums `ModType` and `ModOpts`, fields `path`, `mod_type`, `mod_opts`, `post_mod_stats`, `directory_mod`, `file_mod_data`, `file_mod_location`, `file_mod_len`, and `directory_added_entry`. Private helpers define serialization internals.

Control flow: no runtime flow in the header; it defines which fields are meaningful for different operation types. Comments explain that parent-directory changes are inferred from `kCreateMod` rather than represented as separate directory mods.

State/persistence behavior: `DiskMod` instances are transient C++ objects until serialized into the operation log. They preserve enough state to replay or reason about file ranges and synchronization boundaries.

Dependencies/integration: included by wrappers, utilities, and tests. Risks/test signals: directory modifications are only partially modeled, permissions are TODO, and consumers must understand which enum/field combinations include payload bytes.
