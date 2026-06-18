# sources/sync-backup/git-lfs/t/t-batch-storage-retries.sh

## Purpose
Tests non-rate-limit storage retries and download resume behavior. It covers upload/download server errors, Range resume after interrupted downloads, fallback when a Range request is rejected, and avoiding invalid Range headers for complete or oversized partial files.

## Important APIs, Functions, and Control Flow
Upload/download retry tests set `lfs.transfer.maxretries` and expect exactly two retry messages before success. Range tests remove local objects, create or rely on interrupted partial downloads, run `git lfs fetch`, and inspect `Range`, `206 Partial Content`, `416 Requested Range Not Satisfiable`, accepted/rejected resume logs, and final object integrity. The last test manually creates corrupt `.git/lfs/incomplete/<oid>.part` files to exercise resume validation.

## State, Persistence, and Dependencies
The tests mutate `.git/lfs/objects`, `.git/lfs/incomplete`, local Git config, and trace logs. They depend on object content strings that trigger server behavior, curl verbose headers, and helper assertions for local/server objects.

## Integration Points, Risks, and Test Signals
Integration points are the HTTP storage adapter, transfer queue retry policy, incomplete download resume logic, and hash verification. Signals are retry counts, accepted/rejected Range behavior, OID mismatch errors, and final object store checks. Risks include brittle byte-range calculations and assumptions about temporary file naming.
