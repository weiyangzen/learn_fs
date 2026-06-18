# sources/sync-backup/unison/src/fsmonitor/inotify/Makefile

Purpose: small platform fragment for Linux inotify fsmonitor build inputs.

Important variables: `FSMOCAMLOBJS` lists Lwt, Unix implementation, inotify OCaml modules, watcher common code, and watcher implementation; `FSMCOBJS` includes `inotify_stubs.o`; `FSMOCAMLLIBS=unix.cma`.

Control flow: no rules, only variable definitions consumed by the surrounding build system.

State/persistence: contributes object dependencies for building `unison-fsmonitor`.

Dependencies/integration: integrates with `src/Makefile`/`Makefile.OCaml`, OCaml bytecode objects, and the C inotify stub.

Risks: object ordering can matter for OCaml linking. Missing any Lwt or inotify object breaks fsmonitor builds.

Test signals: Linux `make fsmonitor` and CI build steps that copy `src/unison-fsmonitor`.
