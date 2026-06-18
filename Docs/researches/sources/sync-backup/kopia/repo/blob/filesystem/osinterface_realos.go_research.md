# sources/sync-backup/kopia/repo/blob/filesystem/osinterface_realos.go

Purpose: implements `osInterface` using real operating system calls.

Important APIs/types/functions: `realOS` and methods `Open`, `IsNotExist`, `IsExist`, `IsPathSeparator`, `Rename`, `ReadDir`, `IsPathError`, `IsLinkError`, `Remove`, `Stat`, `CreateNewFile`, `Mkdir`, `MkdirAll`, `Chtimes`, `Geteuid`, and `Chown`.

Control flow: methods mostly wrap standard `os` functions, passing paths through `ospath.SafeLongFilename` for long-path handling. Error classifiers use `os.IsNotExist`, `os.IsExist`, and `errors.As` for `os.PathError`/`os.LinkError`.

State and persistence behavior: this is the production bridge to filesystem state. Create uses `O_CREATE|O_EXCL|O_WRONLY`, rename is the atomic publish step, and chtimes/chown adjust persisted metadata/ownership.

Dependencies/integration points: used by `filesystem.New` unless tests inject an override. Risks include platform-specific long-path behavior, rename semantics across filesystems, and path/link error classification feeding retry decisions. Compile-time interface assertion ensures method coverage; behavior is tested indirectly through filesystem storage tests.
