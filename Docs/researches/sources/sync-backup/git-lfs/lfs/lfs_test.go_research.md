# sources/sync-backup/git-lfs/lfs/lfs_test.go

Purpose: tests current LFS object storage enumeration in temporary repositories.

Important APIs/types/functions: repository helper `NewRepo`, filesystem `EachObject`, `fs.Object`, `lfs.NewPointer`, and pointer sort helpers.

Control flow: first test asserts a new repo has no LFS objects. Second creates a commit with 20 unique files, collects expected pointers from commit helper output, enumerates object storage, converts objects to pointers, sorts both lists, and compares.

State/persistence behavior: creates temp repositories and LFS object files through test commit helpers.

Dependencies/integration: validates filesystem storage integration used by broader LFS commands.

Risks/test signals: does not directly test `Environ` or `LinkOrCopyFromReference`; it tests object presence after repository helper operations.
