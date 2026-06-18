# sources/sync-backup/git-lfs/tools/util_darwin.go

Purpose: macOS clonefile support for efficient copy-on-write file duplication.

Important APIs/types/functions: `cloneFileSupported`, `checkCloneFileSupported`, `CheckCloneFileSupported`, `CloneFileError`, `CloneFile`, `CloneFileByPath`, and `cloneFileSyscall`.

Control flow: init checks OS release major version; support test creates temp src/dst and calls path-based clone; path clone removes existing destination then invokes `unix.Clonefileat` with `CLONE_NOFOLLOW`. Generic writer/reader clone is unsupported on Darwin.

State and persistence: package global caches OS support; test functions create/remove temp files; path clone creates/replaces destination.

Dependencies and integration points: `CopyWithCallback` can use clone support via platform functions; Darwin only supports by path here.

Risks: filesystem-level support can differ from OS version, so syscall can still return unsupported. Existing destination is removed before clone. Error string in test expectations may drift from implementation wording.

Test signals: Darwin tests cover support probing, unsupported generic clone, and path clone content equality when available.
