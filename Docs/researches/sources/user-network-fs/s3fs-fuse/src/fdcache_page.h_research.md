# sources/user-network-fs/s3fs-fuse/src/fdcache_page.h

Purpose: Declares the `fdpage` range record and `PageList` range-map API used to track cache-file loaded/modified byte regions.

Important APIs and types: `fdpage` stores `offset`, `bytes`, `loaded`, and `modified`, with `next()` and `end()` helpers. `fdpage_list_t` is a vector of pages. `PageList::page_status` enumerates unloaded/unmodified, loaded, modified, and loaded+modified states. Public methods cover initialization, resizing, loaded checks, range status updates, unloaded-page extraction, multipart range planning, no-data extraction, dirty-byte accounting, serialization, deserialization, dump, and sparse-file comparison.

Control flow contract: `FdEntity` owns and locks `PageList`; `PageList` itself has no mutex. `size=0` parameters generally mean “to end of list.” `FdEntity` is a friend so it can access `pages` directly for no-cache upload flows.

State and persistence behavior: Header exposes the serializable state shape but persistence happens in `fdcache_page.cpp` through `CacheFileStat`.

Dependencies and integration points: Defines fallback `SEEK_DATA`/`SEEK_HOLE` constants for platforms lacking them. Forward-declares `CacheFileStat` and `FdEntity`.

Risks: The API uses raw `off_t` and `size_t` with sentinel `0` meanings; callers must avoid negative/overflow ranges. Friendship with `FdEntity` bypasses normal encapsulation.

Test signals: `test_page_list.cpp` gives focused unit coverage; integration tests exercise multipart planning and sparse write behavior.
