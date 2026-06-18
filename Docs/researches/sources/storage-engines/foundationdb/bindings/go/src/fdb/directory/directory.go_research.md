# sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/directory.go

## Purpose

`directory.go` defines the public Go directory layer interface, package-level default-root helpers, common errors, version constants, and a small move helper used by directory implementations. It is the main API surface users import for hierarchical FoundationDB subspace management.

## Important APIs, Types, and Functions

The `Directory` interface exposes `CreateOrOpen`, `Open`, `Create`, `CreatePrefix`, `Move`, `MoveTo`, `Remove`, `Exists`, `List`, `GetLayer`, and `GetPath`. Package errors include `ErrDirAlreadyExists`, `ErrDirNotExists`, and `ErrParentDirDoesNotExist`. Version constants encode directory layer metadata version `1.0.0`.

`stringsEqual` compares paths. `moveTo` prevents moving directories across partitions by checking that the new absolute path starts with the current directory layer path, then delegates to `Move` on the relative suffix. The package-level `root` is a directory layer rooted at metadata subspace `0xFE`, content subspace `AllKeys`, and no manual prefixes. Package functions such as `CreateOrOpen`, `Open`, `Create`, `Move`, `Exists`, `List`, and `Root` delegate to that root.

## Control Flow

User code either calls package-level helpers against the default root or obtains a `Directory` and invokes methods relative to that directory. The actual operation flow lives in `directory_layer.go`, `directory_subspace.go`, and partition files; this file defines the common contract and root dispatch.

## State and Persistence Behavior

The default root reserves `0xFE` for directory metadata and allocates content prefixes from the remaining keyspace. Directory operations are transactional through `fdb.Transactor` or `fdb.ReadTransactor`. `Remove` deletes directory metadata and content but cannot prevent already-open clients from writing into a removed prefix later, as documented by the interface.

## Dependencies and Integration Points

The file depends on `fdb` transaction interfaces and `subspace`. It integrates with the rest of the directory package through `NewDirectoryLayer` and implementation types found in sibling files. It is also consumed by stack testers and application code using the Go bindings.

## Risks

The default root can conflict with pre-existing application key partitioning if the database is not otherwise empty or if other data uses `0xFE`. `moveTo` slices `newAbsolutePath[:partition_len]`, so callers must supply paths at least as long as the layer path. Manual prefixes are disabled on the default root, which can surprise users expecting `CreatePrefix` to work globally. Directory removal does not revoke existing subspace handles.

## Test Signals

Tests should verify all interface operations against the default root, layer mismatch errors, parent-missing errors, create-versus-open behavior, move restrictions, recursive removal, list/exist results, root metadata isolation, and interoperability with directory layers from other bindings.
