## sources/security-integrity/libcap/libcap/empty.c

Purpose: minimal executable used by the Makefile to extract the dynamic loader `.interp` string for executable shared-library support.

Important APIs/functions: `main()` returns 0.

Control flow: immediate success.

State/persistence: no runtime state; build uses resulting binary with `objcopy --dump-section .interp`.

Dependencies/integration: C compiler, linker, `objcopy`, `libcap/Makefile` `loader.txt` target.

Risks: if built statically or with unusual linker options, `.interp` may be absent and shared-object executability metadata generation fails.

Test signals: `make -C libcap loader.txt` and verify `loader.txt` contains a dynamic loader path.
