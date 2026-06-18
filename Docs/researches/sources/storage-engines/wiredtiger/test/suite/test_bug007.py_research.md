# sources/storage-engines/wiredtiger/test/suite/test_bug007.py

Purpose: regression test for forced salvage on a file with an invalid header. It confirms normal salvage fails and `force` salvage succeeds.

Important APIs are `session.create`, `session.open_cursor`, direct file overwrite, `session.salvage`, and `assertRaisesWithMessage`. Control flow creates a file object, opens/closes a cursor to ensure the file exists, overwrites the underlying file with repeated random text, asserts plain salvage fails with a `WT_SESSION.salvage` error, then calls salvage with `"force"` and expects success. State behavior is direct corruption of the persistent file followed by recovery/salvage. Dependencies are just `wttest` and `wiredtiger`. Risks include filename mapping assumptions and not verifying resulting contents after forced salvage. Test signals are the expected normal-salvage failure and absence of error from forced salvage.
