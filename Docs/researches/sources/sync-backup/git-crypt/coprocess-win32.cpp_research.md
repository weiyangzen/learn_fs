# sources/sync-backup/git-crypt/coprocess-win32.cpp

Purpose: Windows implementation of `Coprocess`, using Win32 process creation and inheritable pipes to provide command execution compatible with the Unix abstraction.

Important APIs/types/functions: command-line quoting helpers `escape_cmdline_argument` and `format_cmdline`, `spawn_command`, `Coprocess` constructor/destructor, pipe accessors/closers, `spawn`, `wait`, `write_stdin`, and `read_stdout`.

Control flow: pipe accessors create inheritable pipes with `CreatePipe` and mark parent ends non-inheritable with `SetHandleInformation`. `spawn` formats the argument vector into a Windows command line, calls `CreateProcessA` with selected std handles, closes child-side pipe handles in the parent, and stores the process handle. `wait` waits indefinitely and returns the process exit code. Reads treat `ERROR_BROKEN_PIPE` as EOF and retry zero-byte pipe reads.

State/persistence behavior: maintains process and pipe `HANDLE`s plus stream wrappers. The destructor closes streams, pipe handles, and process handle. No durable state is written.

Dependencies/integration: depends on Win32 API, `fhstream`, and `System_error`. It is selected by `coprocess.hpp` when `_WIN32` is defined and underlies all Git/GPG subprocess calls on Windows.

Risks/test signals: Windows argument quoting is subtle, especially trailing backslashes and quotes. The implementation does not expose stderr capture. Tests should include arguments with spaces, quotes, and backslashes; stdin/stdout streaming; child nonzero exit codes; broken pipe EOF; and handle inheritance leaks.
