# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/OpenSearch.cs

## Purpose

Represents an open SMB directory enumeration/search, including cached entries and current enumeration position.

## Important APIs, Types, And Functions

Constructor stores a `List<QueryDirectoryFileInformation>` and `EnumerationLocation`.

## Control Flow

Find-first creates the object with all entries and initial returned count. Find-next slices from `EnumerationLocation`, advances it, and removes the search at end of enumeration.

## State And Persistence Behavior

Session-scoped in-memory search state; it is not refreshed from disk after creation.

## Dependencies And Integration Points

Uses `QueryDirectoryFileInformation`; consumed by SMB1 transaction2 find helpers and SMB2 directory query code.

## Risks And Edge Cases

Cached entries can become stale if the directory changes during enumeration. No internal locking is provided.

## Test Signals

Test find-first/find-next pagination, end-of-search removal, invalid handle lookup, and stale-entry tolerance if files change mid-search.

Source-read signal: reviewed the complete local source file for this item.
