# sources/sync-backup/unison/src/Makefile

Purpose: portable source-level make dispatcher that generates configuration makefiles and delegates real builds to `Makefile.OCaml`.

Important targets: default `all`; BSD `.BEGIN`, Solaris `.INIT`, and generic `Makefile.cfg` rules all run `ocaml make_tools.ml conf` and `conf2`; target set includes `all`, `tui`, `gui`, `macui`, `fsmonitor`, `manpage`, `docs`, `clean`, `depend`, `dependgraph`, and `paths`; developer `tags` target runs etags.

Control flow: generated `Makefile.cfg` and `Makefile2.cfg` are prerequisites for delegated targets. The file avoids directly including freshly generated config because non-GNU make implementations read includes before generating them.

State/persistence: creates `_mk.cfg`, `Makefile.cfg`, `Makefile2.cfg`, build products (`unison`, `unison.exe`, GUI/fsmonitor binaries), and tags.

Dependencies/integration: depends on OCaml, `make_tools.ml`, `Makefile.OCaml`, and make-specific hooks. The trailing fsmonitor object/library definitions look like included fragments for platform-specific fsmonitor builds.

Risks: portability is the primary constraint. Direct inclusion or GNU-only conveniences can break BSD/Solaris/NMAKE. `.NOTPARALLEL` is used because recursive generated configuration is fragile under parallelism.

Test signals: cross-platform CI matrix exercises this file through top-level `make`, `make tui`, `make gui`, `make fsmonitor`, and Windows `nmake`.
