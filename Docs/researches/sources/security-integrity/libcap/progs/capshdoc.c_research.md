# sources/security-integrity/libcap/progs/capshdoc.c

Purpose: checked-in generated data table containing text explanations for Linux capability numbers used by `capsh --explain` and `--suggest`.

Important APIs/types: defines one `static const char *explanationN[]` array per capability and exports `const char **explanations[]` plus `const int capsh_doc_limit`.

Control flow/integration: no executable control flow beyond static initialization. `capsh.c::describe()` indexes this table after `cap_from_name()` and prints the lines. `mkcapshdoc.sh` regenerates the file from `../doc/values/*.txt` and capability names, and the Makefile diffs generated output against this checked-in copy.

State and dependencies: no runtime mutation. Depends on alignment with `cap_names.list.h` and documentation value files.

Risks and test signals: stale or misordered entries produce misleading privilege explanations. The build target `capshdoc.c.cf` is the primary drift detector.
