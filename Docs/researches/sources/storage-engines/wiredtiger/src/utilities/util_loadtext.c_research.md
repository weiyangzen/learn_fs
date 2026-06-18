## sources/storage-engines/wiredtiger/src/utilities/util_loadtext.c

Purpose: implements `wt loadtext`, a simpler loader for flat text records into existing string-value row-store or record-number column-store objects.

Important APIs/types/functions: `util_loadtext` parses `-f` and a single URI. Static `text` opens a cursor with `append,overwrite`, validates formats, and calls static `insert`. `insert` reads key/value or value-only lines using `util_read_line` and inserts them through the cursor.

Control flow: optional `-f` redirects stdin. The command normalizes one URI with `util_uri`, then `text` opens a cursor. It requires `value_format == "S"` and key format either `"S"` or `"r"`. Row-store string keys read alternating key and value lines; record-number keys read only values and append them. After insertion it closes the cursor and flushes the URI.

State and persistence behavior: inserts or overwrites records in an existing object and flushes on success. For record-number column stores it appends new recnos. For string-key row stores it overwrites matching keys because the cursor was opened with overwrite.

Dependencies and integration points: uses public cursor insert, dump/text line decoding, `util_uri`, `util_flush`, and global verbose progress output. It is dispatched by `util_main.c`, which opens the connection with `create` even though the target object must already exist.

Risks: only supports simple string values and string or record-number keys. Input is line-oriented, so embedded newlines require whatever escaping `util_read_line` supports. On read errors inside `insert`, allocated buffers are not freed on the immediate return paths before the function exits, which is a small leak in a short-lived utility process. Partial loads remain if a later line or insert fails.

Test signals: loadtext into string-key tables with alternating lines, loadtext into record-number tables with value-only lines, format rejection for non-string values or unsupported key formats, file redirection errors, verbose progress every 100 inserts, cursor close/flush failure, and partial input EOF behavior.
