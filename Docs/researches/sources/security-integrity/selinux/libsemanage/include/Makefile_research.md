# sources/security-integrity/selinux/libsemanage/include/Makefile

Purpose: installs libsemanage public headers into the configured include tree. It is intentionally minimal because header generation and compilation happen in `src/Makefile`.

Important APIs/targets: variables are `PREFIX` and `INCDIR`, defaulting to `/usr` and `$(PREFIX)/include/semanage`. The `install` target creates `$(DESTDIR)$(INCDIR)` and installs every `semanage/*.h` file mode `0644`. `all` is a no-op.

Control flow: a packaging build descends into this directory, invokes `make install`, creates the include directory if needed, and copies the header set with `install`.

State and persistence behavior: writes only installed header files under `DESTDIR`; it does not generate headers or track dependency timestamps beyond make's target execution.

Dependencies and integration points: used by top-level SELinux userspace packaging and depends on the public header directory layout. It must stay aligned with `src/libsemanage.pc.in` include paths and the umbrella `semanage.h` header.

Risks: `$(wildcard semanage/*.h)` silently omits missing headers and includes any accidental header added in that folder. Test signals are staged installs verifying the complete public ABI header set and correct destination paths.
