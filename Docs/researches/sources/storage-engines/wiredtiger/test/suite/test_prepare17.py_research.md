# sources/storage-engines/wiredtiger/test/suite/test_prepare17.py

## Purpose

Regression test for cache-stuck behavior when committing a large prepared update that itself exceeds eviction trigger thresholds.

## Important APIs, Control Flow, and State

The connection is configured with 1 MB cache and low eviction dirty/update triggers. The test inserts a 400 KB value inside a transaction, prepares at timestamp 5, assigns commit and durable timestamps, closes the cursor, sleeps to give eviction time to write prepared content, and then commits. The important state is that commit may need to read the prepared page and history-store page back into cache while the cache already appears over target.

## Dependencies, Risks, and Test Signals

Dependencies are timing/sleep, eviction thresholds, and prepare commit. The risk is eviction checks during prepared transaction resolution causing a stuck cache or deadlock. The test signal is successful commit under pressure; it is primarily a no-hang/no-crash regression.
