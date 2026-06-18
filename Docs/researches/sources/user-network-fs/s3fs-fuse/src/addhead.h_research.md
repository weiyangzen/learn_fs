<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/addhead.h -->
# sources/user-network-fs/s3fs-fuse/src/addhead.h

Purpose: Declares the additional HTTP header rule structures and `AdditionalHeader` singleton interface.

Important APIs and types: `RegexPtr` is a `std::unique_ptr<regex_t, regfree>` for RAII regex cleanup. `add_header` owns an optional regex, base string, header key, and header value; copy operations are deleted and moves are partially supported. `addheadlist_t` is a vector of rules. `AdditionalHeader` exposes `get`, `Load`, `Unload`, two `AddHeader` overloads, and `Dump`.

Control flow and integration: Callers use `AdditionalHeader::get()` to load rules from an `ahbe_conf` path, then ask it to augment metadata maps or curl slists for individual object paths. The singleton is function-local static to avoid global initialization ordering problems.

State and persistence: Holds process-local enabled flag and rule vector. Persistent state is external configuration only.

Dependencies: Includes C++ memory/string/vector/utility, POSIX `regex.h`, and `metaheader.h`; the curl slist overload forward-references `struct curl_slist`.

Risks: `add_header& operator=(add_header&&) = delete` means vector operations rely on move construction and no move assignment. Header insertion semantics are implemented in the cpp and use map overwrite behavior. Singleton makes tests order-dependent unless `Unload` is called between cases.

Test signals: Compile coverage for move-only vector behavior, singleton lifecycle tests, and functional tests through `addhead.cpp`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/addhead.h -->
