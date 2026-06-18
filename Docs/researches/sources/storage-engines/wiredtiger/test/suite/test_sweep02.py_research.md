<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_sweep02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_sweep02.py

Purpose: basic configuration smoke tests for file-manager sweep options at connection open.

Important APIs/types/functions: `test_sweep02` overrides setup hooks to manage connections manually and uses `wiredtiger_open` with `create` plus `file_manager` configs. Constants define a test home `WT_TEST` and table URI but active tests only open connections.

Control flow: five tests open a connection with empty `file_manager=()`, `close_scan_interval=1`, `close_idle_time=1`, `close_handle_minimum=500`, and a combination of scan interval plus idle time.

State and persistence behavior: opening a home with each config validates config parsing and initialization; no table data is created.

Dependencies/integration points: covers connection configuration admission for sweep/file-manager settings. Risks are low; signal is successful connection open without exceptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_sweep02.py -->
