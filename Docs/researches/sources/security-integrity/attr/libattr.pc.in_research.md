## sources/security-integrity/attr/libattr.pc.in

Purpose: pkg-config template for libattr consumers.

It substitutes prefix, libdir, includedir, version, and emits `Cflags` plus `Libs: -lattr`. State is installed `libattr.pc`. Dependencies are configure substitutions. Risks are missing private libraries if link requirements change. Test signal is `pkg-config --cflags --libs libattr` after install.
