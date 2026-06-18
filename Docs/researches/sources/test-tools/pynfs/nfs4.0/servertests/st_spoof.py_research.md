# sources/test-tools/pynfs/nfs4.0/servertests/st_spoof.py

Purpose: Manual/security-oriented tests for spoofing user access or filehandles, using supplied `--usefile`, `--uid`, `--gid`, and `--usefh` options.

Important APIs/types/functions: Uses `environment.check` and client helpers `open_confirm`, `read_file`, `write_file`, and `close_file`. `_convert` decodes command-line filehandle strings containing `\xhh` escape sequences into raw bytes.

Control flow: `testSpoofUser` reads and writes a configured file through opens with read and write access. `testSpoofFhRead` and `testSpoofFhWrite` convert an externally supplied filehandle and attempt direct I/O using stateid zero/defaults.

State and persistence behavior: Mutates the configured target file in spoof-user and spoof-write tests. Direct filehandle tests may access objects outside the normal test tree if a user supplies such a handle.

Dependencies and integration points: Requires explicit test options and server/export security configuration. These tests are not safe generic conformance tests; they are diagnostic probes.

Risks: Can overwrite user-selected files. `_convert` uses `eval` to parse hex escapes and returns a text string in Python 3 style code, which can be unsafe/incorrect for raw bytes. The module assumes the user intentionally supplies sensitive paths/handles.

Test signals: Success or failure comes from `check()` around read/write/close operations; no specific error status is asserted for spoof blocking.
