# sources/sync-backup/unison/Makefile

Purpose: portable top-level Unison make entrypoint compatible with GNU Make, BSD make, Solaris make/dmake, and NMAKE.

Important targets: `all` builds `src` and `manpage`; `src` recursively invokes `$(MAKE)` in `src`; `tui`, `gui`, `macui`, `fsmonitor`, `manpage`, `docs`, `clean`, and `depend` delegate to `src`; `test` runs `ocaml src/make_tools.ml run ./src/unison -ui text -selftest`; `install` runs `ocaml src/make_tools.ml install`.

Control flow: intentionally recursive and `.NOTPARALLEL` because portability requires multiple recursive make invocations. `FRC` is used for phony-like behavior on make implementations that do not handle `.PHONY` consistently.

State/persistence: build outputs are created under `src`, docs/manpage outputs through delegated targets, and install writes through `make_tools.ml` according to install variables.

Dependencies/integration: relies on `src/Makefile`, OCaml, `src/make_tools.ml`, and platform make semantics.

Risks: parallelism is disabled at the top level to avoid recursive-make races. Any edit here must preserve non-GNU syntax portability; even convenient GNU-only features can break supported build environments.

Test signals: `make`, `make tui`, `make gui`, `make fsmonitor`, `make test`, and `make install DESTDIR=...` are the relevant checks across supported make implementations.
