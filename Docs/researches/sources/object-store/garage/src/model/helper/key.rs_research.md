# sources/object-store/garage/src/model/helper/key.rs

## Purpose
This file provides small key-table lookup helpers around `Garage`, separating internal retrieval from user-facing existing-key retrieval.

## Important APIs, types, and functions
`KeyHelper` wraps `&Garage`. `get_internal_key` returns a `Key` table entry even if deleted and treats missing rows as internal errors. `get_existing_key` returns only non-deleted keys and maps missing/deleted rows to `Error::NoSuchAccessKey`.

## Control flow
Both methods perform quorum reads through `key_table.get(&EmptyKey, key_id).await`. The internal variant uses `ok_or_message`, while the existing variant filters `!state.is_deleted()`.

## State and persistence behavior
This module is read-only. It observes the fully replicated key table and does not mutate access-key state.

## Dependencies and integration points
It depends on `garage_table::util::EmptyKey`, `garage_util::error::OkOrMessage`, helper errors, `Garage`, and `Key`. `LockedHelper` uses it for alias/permission mutations and delete flows.

## Risks and edge cases
The distinction between missing internal key and deleted key is important: internal mutation/repair flows need tombstones, while user-facing operations should hide deleted keys. Callers pass `String` references rather than `str`, matching table key types but requiring ownership conversions elsewhere.

## Test signals
No direct tests. Useful tests should cover existing/deleted/missing keys and helper integration in permission and local-alias mutation paths.
