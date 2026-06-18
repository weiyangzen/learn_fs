<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucNList.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucNList.cc

Purpose: Implements wildcard-capable name list entries and thread-safe anchor replacement logic.

APIs and control flow: The entry constructor duplicates the configured name and splits the first `*` into left and right fragments. `NameKO()` performs case-insensitive matching, while `NameOK()` performs case-sensitive matching. Both support exact, prefix-only, suffix-only, and prefix/suffix wildcard forms. `XrdOucNList_Anchor::Replace()` updates an existing equivalent wildcard entry or inserts a new one ordered by decreasing left-fragment length.

State and persistence: Each entry owns its duplicated name buffer; wildcard right fragments point into that same allocation. The anchor owns a mutex and list head but does not persist state outside memory.

Dependencies and integration: Depends on `XrdSysMutex` for anchor operations. Used by components that need dynamic allow/deny or pattern-to-flag lists.

Risks and test signals: Only the first `*` is special. Case-sensitive and case-insensitive APIs have different semantics. Tests should cover replacement ordering, wildcard edges, duplicate replacement, concurrent anchor methods, and destructor cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucNList.cc -->
