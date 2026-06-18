# sources/security-integrity/libcap/pam_cap/lazylink.c

Purpose: build/link probe used to test whether the selected link flags support lazy linking for an executable shared object.

Important APIs/functions: declares unresolved `nothing_sets_this()` and defines `nothing_uses_this()` that calls it. The `SO_MAIN()` exits successfully without calling `nothing_uses_this()`.

Control flow: if lazy linking is available, the process can start and exit despite the unresolved symbol path being unused. If link/runtime resolution is eager in the tested configuration, the build or execution exposes that.

State and dependencies: no runtime state. Depends on `execable.h` and the linker/loader behavior under test.

Risks and test signals: intentional unresolved symbol usage can look suspicious to static analysis but is the point of the probe. A failure signals loader/linker assumptions for executable shared modules are not met.
