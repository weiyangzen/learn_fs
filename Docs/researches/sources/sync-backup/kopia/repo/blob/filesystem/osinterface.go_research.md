# sources/sync-backup/kopia/repo/blob/filesystem/osinterface.go

Purpose: defines the filesystem provider's OS abstraction to make file operations mockable.

Important APIs/types/functions: `osInterface`, `osReadFile`, and `osWriteFile`. The interface covers open/stat/read-dir/create/remove/rename/mkdir/chown/chtimes/error classification and effective UID. Read files must support read/seek/close/stat; write files must support write/close/sync.

Control flow: no runtime logic is implemented here. `fsImpl` calls this interface for all OS interactions, and tests provide mock implementations.

State and persistence behavior: the interface abstracts persistent filesystem state but stores none itself.

Dependencies/integration points: implemented by `realOS` and `mockOS`. Risks include interface bloat making mocks tedious, provider behavior depending heavily on correct error classification, and missing operations such as directory fsync. Tests around mock and real OS implementations validate enough of the contract for filesystem storage error paths.
