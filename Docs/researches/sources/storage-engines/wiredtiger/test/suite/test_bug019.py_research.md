# sources/storage-engines/wiredtiger/test/suite/test_bug019.py

Purpose: regression that log preallocation only keeps a small moving range of prepared log files, originally targeting accumulation on Windows directory-list handling.

Important APIs/types/functions: `wiredtiger.stat`, `statistics:` cursor, `stat.conn.log_prealloc_used`, `stat.conn.log_prealloc_max`, `session.checkpoint`, `fnmatch.filter`, `os.listdir`, and timing loops.

Control flow: create a logged table with 100KB log file max; populate enough 2KB values to churn many log files and increase `log_prealloc_max`; wait for `*Prep*` files; loop 9 times ensuring `log_prealloc_used` advances after each populate/checkpoint; finally wait up to 90 seconds for the preallocation max to drop below its observed maximum.

State/persistence behavior: writes many unique keys and checkpoints to force log allocation, use, and cleanup. The relevant persistent artifacts are log files and preallocated `Prep` files.

Dependencies/integration: relies on logging subsystem statistics, background log server timing, and filesystem visibility.

Risks/test signals: timing-sensitive, with 90-second waits to reduce flake. Failures indicate no preallocation, nonmoving preallocation use, or failure to shrink when idle.
