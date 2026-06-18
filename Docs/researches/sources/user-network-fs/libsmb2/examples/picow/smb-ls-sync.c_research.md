# sources/user-network-fs/libsmb2/examples/picow/smb-ls-sync.c

Purpose: This file is currently empty. Its name suggests it may have been intended as a C version of the Pico W synchronous SMB listing example, but the functional implementation lives in `examples/picow/main.cpp`.

Important APIs and types: There are no declarations, functions, includes, or build-system references visible in the empty file.

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: The file can only matter if a build system or external documentation references it directly. The local Pico CMake file builds `main.cpp`, not this file.

Risks: Empty source files can confuse researchers or users looking for the implementation implied by the filename. If it is accidentally added to a target, it contributes no symbols.

Test signals: `wc -l` reports zero lines. Build validation should confirm no target expects symbols from this file.
