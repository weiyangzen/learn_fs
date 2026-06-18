# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncdirenum.c

This file implements directory enumeration virtualization. It suppresses the real mapping from listings and injects a synthetic user mapping entry when enumerating relevant parent directories.

`NcEnumerateDirectory` handles `IRP_MN_QUERY_DIRECTORY` in pre-operation. It:
- Determines structure offsets for the requested directory information class.
- Gets the instance context and opened directory name.
- Compares the directory against user and real mappings.
- Passes through unless the enumerated directory is the parent of either mapping.
- Allocates/attaches a stream handle context.
- Serializes per-handle enumeration with `EnumerationOutstanding`.
- Sets up or resets enumeration state through `NcStreamHandleContextEnumSetup`.
- Populates an internal cache from the filesystem using `NcPopulateCacheEntry`.
- Chooses between cached filesystem entries and a synthetic injection entry with `NcDirEnumSelectNextEntry`.
- Skips real mapping entries with `NcSkipName`.
- Copies selected entries into the caller’s buffer with `NcCopyDirEnumEntry`.
- Completes the query itself with success, `STATUS_NO_SUCH_FILE` on first empty query, or `STATUS_NO_MORE_FILES` later.

`NcEnumerateDirectorySetupInjection` builds the synthetic user mapping entry. It checks the caller’s search pattern first; if neither the long nor short user final component matches, no injection is needed. Otherwise it opens the real mapping parent, queries the real mapping entry, rewrites the entry’s long and short names to the user mapping names, and stores the result as `InjectionEntry`.

`NcPopulateCacheEntry` reads ahead from the underlying filesystem into a paged-pool buffer. Empty filesystem statuses are converted to success with an empty cache so the merge logic can still return an injection entry if present.

`NcDirEnumSelectNextEntry` preserves approximate sort order by comparing the current cached filesystem entry name with the injection entry name and returning whichever sorts first.

`NcSkipName` suppresses the real mapping final component when enumerating the real mapping parent. It advances or frees the cache entry as needed.

`NcCopyDirEnumEntry` copies one entry into the user buffer, advances the source cache, and fixes `NextEntryOffset` when an entry becomes the last visible entry.

`NcStreamHandleContextEnumSetup` records the first search string and information class for a handle, enforces consistent information class on later queries, resets caches on first use or restart, and prepares injection when enumerating the user mapping parent.

`NcStreamHandleContextEnumClose` frees cached directory-entry buffers and saved search string.

Important dependencies:
- Offset accessors/mutators from `ncoffsets.c` let the code work across multiple directory information classes.
- `NcQueryDirectoryFile` comes from `nccompat.c`.
- Stream handle context allocation and locking come from `nccontext.c`.
- Search matching uses `FsRtlIsNameInExpression`.

Notable behavior:
- Multiple outstanding enumeration requests on the same handle are rejected with `STATUS_UNSUCCESSFUL`; the file has a TODO to improve this.
- The implementation is pre-operation and completes user queries itself rather than post-processing filesystem output.
- The code tries to preserve enumeration ordering while merging a single virtual entry.
- Pool tag usage is inconsistent in a few free paths: some buffers allocated with directory-query tags are freed with `NC_TAG`, while other paths use the specific tags.
