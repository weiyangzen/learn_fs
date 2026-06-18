# sources/sync-backup/syncthing/lib/scanner/virtualfs_test.go

## Purpose
Provides fake filesystem implementations and file/info types for scanner tests that need large or synthetic directory trees without real disk data.

## Important APIs, Types, and Functions
`infiniteFS` simulates a configurable tree width/depth with fixed-size files. `singleFileFS` simulates a filesystem containing one file. `fakeInfo` implements scanner filesystem file-info methods. `fakeFile` implements file read/stat/close methods and returns unsupported errors for writes, seeks, and truncation. `errNotSupp` marks unsupported operations.

## Control Flow
`infiniteFS.DirNames` returns file names first and directory names while below configured depth, allowing scanner tests to see files before deep traversal. `fakeFile.Read` advances a read offset and returns EOF at the configured size. `singleFileFS` returns root and one named file, erroring on other paths.

## State and Persistence Behavior
State is in-memory configuration and `fakeFile.readOffset`. No disk state exists. Reads return zero-filled byte slices by not modifying the supplied buffer, which is acceptable for hashing deterministic synthetic content.

## Dependencies and Integration Points
Depends on scanner filesystem interfaces from `lib/fs` and protocol platform data. These fakes support scanner walk/hash tests elsewhere, especially scalability and virtual filesystem behavior.

## Risks and Edge Cases
The fakes only implement the methods needed by tests and return generic errors for unsupported operations. `fakeInfo.IsDir` classifies any basename containing `dir` as a directory, which is convenient but artificial. Read data is all zero bytes, so tests using these fakes should not assume varied content.

## Test Signals
Compile-time interface compatibility and downstream scanner tests using these fakes are the signals. This file itself defines no test functions.
