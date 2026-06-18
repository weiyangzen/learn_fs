# sources/storage-engines/wiredtiger/test/suite/test_prepare32.py

## Purpose

Tests checkpoint behavior for committed prepared updates as stable timestamp advances across prepare, commit, and durable timestamps.

## Important APIs, Control Flow, and State

After initial data and a clean checkpoint, the test prepares updates for keys 1 to 99 at timestamp 70 with a prepared ID and commits at timestamp 80 with durable timestamp 90. With stable still 40, checkpoint should not write prepared content. Stable 85 should write the update as prepared. Stable 95 should write it as committed with durable start timestamp metadata and no prepared time window. Stable 100 should not rewrite because the page is clean.

## Dependencies, Risks, and Test Signals

Dependencies include preserve-prepared base behavior, `checkpoint_and_verify_stats`, and `wiredtiger.stat.dsrc` counters for prepared and durable start timestamps. Risks are premature prepared writes, failure to convert prepared cells to committed cells, or dirty-page churn. Signals are staged stat checks across stable timestamp movement.
