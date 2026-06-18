# sources/storage-engines/wiredtiger/test/suite/test_prepare04.py

## Purpose
Tests prepared update conflict behavior for readers and writers with different read timestamps and `ignore_prepare` settings.

## APIs, Types, And Functions
Defines `test_prepare04` with row/column scenarios, read-before/read-after/no timestamp scenarios, and `ignore_prepare` true/false scenarios. It uses `prepare_transaction`, alternate sessions, cursor search/update, conflict regexes, and timestamped commit.

## Control Flow, State, And Persistence
The test creates a table, commits a base value at timestamp 100, advances oldest to 100, then prepares an update at timestamp 200. A second session begins with the scenario transaction config. If the reader is after the prepare timestamp and `ignore_prepare=false`, search must raise a prepared conflict; otherwise it sees the old value. A write attempt from the second session must always detect a concurrent operation conflict. The prepared update is then committed.

## Dependencies, Integration, Risks, And Test Signals
Depends on timestamp visibility, prepared conflict detection, and `ignore_prepare`. Risks are hiding prepared conflicts from readers that should block or allowing conflicting writers. Signals are expected prepared-conflict and concurrent-conflict errors plus old-value visibility in allowed cases.
