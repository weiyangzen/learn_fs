<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_file.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_file.cpp

Purpose: Tests block open/close behavior, configuration parsing, block hash reference management, file handle setup, and read-only/sync close paths.

Important APIs/types/functions: Validation helpers check `WT_BLOCK`, `WT_FH`, config-derived fields, connection block lock state, and hash removal. Tests call `__wt_block_manager_create`, `__wt_block_open`, `__wti_bm_close_block`, and `__wt_block_manager_drop`.

Control flow: Opens the same file twice to check reference counts, closes handles, tries allocation-size and block-allocation config variants, validates missing config failures, and tests read-only and sync-on-close paths.

State and persistence behavior: Creates `test.wt` and `test2.wt`, mutates connection block hash and block file references.

Dependencies and integration points: Uses `mock_session`, `config_parser`, filesystem current path, block manager internals, and connection block lock.

Risks and test signals: Disabled null-close segmentation test and FIXME around free pattern show known fragility. Signals include no leaked block hash entries, correct ref counts, and unlocked connection block lock after operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_file.cpp -->
