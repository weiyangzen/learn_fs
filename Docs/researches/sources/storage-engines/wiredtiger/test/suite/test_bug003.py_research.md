# sources/storage-engines/wiredtiger/test/suite/test_bug003.py

Purpose: regression test confirming a bulk-load cursor can be opened after a checkpoint, including named and unnamed checkpoint scenarios, for file and table objects.

Important APIs are `session.create`, `session.checkpoint`, `session.open_cursor(..., "bulk")`, and scenario generation. Control flow creates either `file:data` or `table:data`, performs either a default checkpoint or named checkpoint `ckpt`, then opens a bulk cursor on the object. There are no inserts through the bulk cursor; the signal is that checkpoint state does not prevent bulk cursor creation. State behavior is checkpoint metadata and object state before initial bulk load. Dependencies are minimal (`wttest`, `make_scenarios`). Risks include narrow assertion surface: it detects open failures but not correctness of subsequent bulk inserts. Test signal is successful bulk cursor open after checkpoint.
