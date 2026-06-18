## sources/security-integrity/libcap/libcap/libpsx.pc.in

Purpose: pkg-config template for installed libpsx, including special linker flags needed to force the psx archive into consumers.

Important fields: standard pkg-config variables plus `Libs` using `--no-as-needed`, `--whole-archive -lpsx`, `--no-whole-archive`, `--as-needed`, and `-lpthread`.

Control flow: substituted by `libcap/Makefile` to produce `libpsx.pc`.

State/persistence: template only; generated `.pc` file is installed.

Dependencies/integration: pkg-config, linker behavior for static archive constructors/wrappers, pthreads.

Risks: linker flag ordering is critical; distributions/toolchains may handle whole-archive/as-needed differently.

Test signals: build threaded consumer using `pkg-config --libs libpsx`, verify libpsx overrides libcap syscall hooks at runtime.
