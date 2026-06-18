# sources/sync-backup/git-crypt/coprocess-win32.hpp

Purpose: Windows declaration of the `Coprocess` class.

Important APIs/types/functions: fields for process, stdin, and stdout `HANDLE`s; stream pointers; static read/write callbacks; disabled copy/assignment; public pipe, spawn, and wait methods.

Control flow: declares the same lifecycle as the Unix header: request pipes, spawn process, close pipe ends, wait for exit.

State/persistence behavior: state is OS handle ownership and stream wrapper ownership. No persistent files are managed here.

Dependencies/integration: includes `fhstream.hpp`, `<windows.h>`, and `<vector>`. Used through `coprocess.hpp`.

Risks/test signals: handle cleanup and inheritance flags are the key correctness areas. Tests should check repeated subprocess creation without leaked handles and parity with Unix behavior for command execution helpers.
