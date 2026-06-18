# sources/storage-engines/wiredtiger/examples/python/ex_access.py

Purpose: Python binding equivalent of the simple access example.

Important APIs and control flow: removes and recreates `WT_HOME`, opens a connection with `wiredtiger_open('WT_HOME', 'create')`, opens a session, creates `table:T` with string key/value formats, opens a cursor, inserts `key1/value1` using `set_key`, `set_value`, and `insert`, resets the cursor, iterates it with Python cursor iteration, prints records, and closes the connection.

State and persistence: recreates a local WT_HOME and persists one table/record. Cursor iteration wraps WiredTiger cursor movement in Python binding semantics.

Dependencies and integration: depends on the Python `wiredtiger` module and filesystem access. Snippet markers are documentation-oriented.

Risks: `os.system('rm -rf WT_HOME')` is destructive relative to the working directory. The script does not use `try/finally`, so failures can leave handles open until process exit.

Test signals: execution should print `Got record: key1 : value1` and close cleanly.
