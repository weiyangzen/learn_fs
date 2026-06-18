# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzonePrefixPathImpl.java

## Purpose
`OzonePrefixPathImpl` implements the ACL-facing `OzonePrefixPath` abstraction for a volume/bucket/key prefix. It resolves the prefix status and can lazily iterate child paths in batches through `KeyManager`.

## Important APIs, types, and functions
- The constructor builds a head `OmKeyArgs`, retrieves the file status, translates `FILE_NOT_FOUND` to `KEY_NOT_FOUND` for legacy caller compatibility, and sets `checkRecursiveAccess` when a directory has children.
- `getOzoneFileStatus()` returns the resolved prefix status.
- `getChildren(String)` returns a `PathIterator`.
- `PathIterator` batches `keyManager.listStatus(...)`, rejects a file prefix where a directory is expected, removes duplicate continuation entries, and advances using the previous returned trimmed name.
- `isCheckRecursiveAccess()` indicates whether recursive ACL checks are needed for non-empty directories.

## Control flow
Construction validates the prefix and determines whether recursive access checks are meaningful. Child iteration starts with `prevKey=""`, then `hasNext()` fetches the next batch only after the current iterator is exhausted and a current value exists. `next()` delegates to `hasNext()` and throws `NoSuchElementException` at end.

## State and persistence behavior
The object stores volume, bucket, `KeyManager`, batch size, initial path status, and recursive-check flag. It does not persist or mutate metadata; it reads file status, child status lists, and child-existence information from `KeyManager` and `OMFileRequest`.

## Dependencies and integration points
It integrates native ACL checks with OM key/file metadata by implementing `OzonePrefixPath`. It depends on `KeyManager`, `OmKeyArgs`, `OzoneFileStatus`, `OMFileRequest.hasChildren`, `OMException`, and Commons `StringUtils`.

## Risks and edge cases
`hasNext()` suppresses `IOException` by logging at debug and returning false, which can make permission or metadata errors look like end-of-iteration. The fixed batch size of 1000 is not configurable. Duplicate continuation removal mutates the returned list. File prefixes are rejected only when the first batch contains exactly the file status matching the requested prefix.

## Test signals
Tests should cover constructor translation from `FILE_NOT_FOUND` to `KEY_NOT_FOUND`, directory child detection, empty directory recursive flag, file prefix rejection in `PathIterator`, paginated listing with duplicate start-key removal, iteration across multiple batches, and iterator behavior when `listStatus` throws.
