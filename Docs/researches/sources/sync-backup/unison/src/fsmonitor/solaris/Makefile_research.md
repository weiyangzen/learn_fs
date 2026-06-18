# sources/sync-backup/unison/src/fsmonitor/solaris/Makefile

Purpose: Solaris/illumos fsmonitor build fragment.

Important variables: `FSMOCAMLOBJS` includes Lwt, generic Unix Lwt implementation, watcher common code, `ubase/safelist.cmo`, and the Solaris watcher; `FSMCOBJS` includes `fen_stubs.o`; `FSMOCAMLLIBS=unix.cma`.

Control flow: variable-only make fragment consumed by the main build.

State/persistence: controls which OCaml and C objects are linked into the fsmonitor binary on Solaris-like platforms.

Dependencies/integration: relies on Solaris event ports/FEN C stubs and OCaml watcher modules.

Risks: object list must stay synchronized with watcher implementation dependencies; portable make syntax is required.

Test signals: Solaris/illumos `make fsmonitor` and runtime file-event tests.
