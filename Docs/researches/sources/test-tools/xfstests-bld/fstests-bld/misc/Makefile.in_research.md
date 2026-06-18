# sources/test-tools/xfstests-bld/fstests-bld/misc/Makefile.in

Purpose: `misc/Makefile.in` builds and installs local benchmark/test utilities for fstests-bld.

Important APIs, types, and functions: variables `CC`, `CFLAGS`, `LDFLAGS`, `PROGS=fname_benchmark postmark resize syncfs`, and `SCRIPTS=encrypt-fname-benchmark`. Targets include `all`, individual binaries, `install`, `zerofree`, `clean`, and regenerated `Makefile`.

Control flow: `all` builds `PROGS`. Each C target invokes `$(CC) $(LDFLAGS) -o <prog> -O2 $<`. `install` copies programs and scripts to `$(DESTDIR)/bin` and chmods executable. `zerofree` links against `-lext2fs`. `Makefile` regeneration calls top-level `config.status`.

State and persistence: creates local binaries and installs them under `DESTDIR`. `clean` removes configured program outputs and `zerofree`.

Dependencies and integration points: generated from `configure`/`configure.ac`. Depends on source files not all in this work item (`resize.c`, `syncfs.c`, zerofree source). Integrates benchmark utilities into fstests appliance images.

Risks: `CFLAGS` is defined but not used in compile commands; only `-O2` is passed. `all` does not build `zerofree`. Install assumes binaries/scripts exist and does not preserve modes except chmod +x.

Test signals: configure then `make -C misc all install DESTDIR=...`, verify binaries execute/help, and `make clean` removes outputs.
