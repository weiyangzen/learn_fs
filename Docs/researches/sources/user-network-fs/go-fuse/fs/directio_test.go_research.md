# sources/user-network-fs/go-fuse/fs/directio_test.go

Purpose: tests `FOPEN_DIRECT_IO` read and file-handle `Lseek` behavior.

Important types/functions: `dioRoot.OnAdd` adds `file`; `dioFile.Open` returns `dioFH` with `FOPEN_DIRECT_IO`; `dioFH.Read` returns bytes encoding the offset; `dioFH.Lseek` rounds offsets up to the next 1024-byte boundary. `TestFUSEDirectIO` reads initial bytes, conditionally tests kernel lseek support, and verifies subsequent read starts at offset 1024.

State/dependencies: real FUSE mount and kernel protocol support for lseek 7.24.

Risks/test signals: covers direct I/O bypassing cache and file-handle operation dispatch. It skips lseek assertions when unsupported.
