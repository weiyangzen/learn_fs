<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/util_block.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/util_block.cpp

Purpose: Shared Catch2 helper implementations for block manager tests.

Important APIs/types/functions: Validates and frees `WT_EXT`/`WT_SIZE` nodes and caches; `create_write_buffer` prepares aligned write buffers with block header space; `setup_bm` initializes mock block manager file operations, creates/opens a block file, installs block manager methods, parses config, and initializes checkpoint extent lists; `test_and_validate_write_size` checks allocation-size rounding.

Control flow: Helpers use `REQUIRE` assertions, allocate WiredTiger buffers, set up actual block files, and validate cache chains.

State and persistence behavior: Creates backing files via `__wt_block_manager_create`, opens `WT_BLOCK`, mutates `WT_BM`, `WT_BLOCK_MGR_SESSION`, and `WT_ITEM` buffers.

Dependencies and integration points: Used by block API/session tests; depends on `mock_session`, `config_parser`, and WiredTiger block internals.

Risks and test signals: Because helpers assert internally, failures point here even when caller logic is wrong. Buffer sizing assumes `write_size` always rounds up one allocation unit.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/util_block.cpp -->
