## sources/security-integrity/attr/examples/Makefile

Purpose: standalone example build file for `copyattr`.

It compiles with debug/warnings, includes `../include`, links `-lattr`, and supports `all` and `clean`. State is the produced `copyattr` binary. Dependencies are a compiler and installed or findable libattr. Risks include assuming library search paths and not using the main build system variables. Test signal is building the example manually.
