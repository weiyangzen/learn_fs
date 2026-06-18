# sources/storage-engines/wiredtiger/test/suite/test_dictionary03.py

Purpose: tests dictionary reuse when a repeated value also has time-window validity metadata.

Important APIs and control flow: row and variable-column scenarios create a dictionary-compressed file, set oldest and stable timestamps, write two base values, then begin a transaction and write a third key with the first value at commit timestamp 20. After checkpoint, it reads `stat.dsrc.rec_dictionary`.

State and persistence: timestamped transaction metadata becomes part of the reconciled cell. The checkpoint forces the time-window-bearing cell through dictionary compression.

Dependencies and integration: uses `make_scenarios`, `simple_key`, timestamp helpers from `wttest`, and dsrc statistics.

Risks and test signals: the expected dictionary reuse count is exactly one. Failure indicates time-window metadata prevented valid dictionary reuse or statistics accounting changed.
