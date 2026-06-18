# sources/sync-backup/unison/doc/Makefile

Purpose: portable makefile for generating Unison manual outputs and OCaml embedded help strings.

Important targets/variables: `all` builds `unison-manual.pdf`, `.html`, `.txt`, and `../src/strings.ml`; `m=unison-manual`; `DRAFT=false`; includes `../src/Makefile.ProjectInfo`; `SOURCES` includes manual TeX, local/short TeX, generated version/preferences files; `HEVEA_FOUND` gates HeVeA-dependent outputs.

Control flow: writes `unisonversion.tex` from `VERSION`, generates separate directive files for text and non-text builds, uses HeVeA plus lynx to make text, uses `docs.ml` to derive `strings.ml`, runs `pdflatex` twice in draft mode for aux/toc and once for PDF, uses HeVeA for HTML, and generates preference listings by running `../src/$(NAME)`.

State/persistence: creates TeX aux/toc/log files, manual `.pdf/.html/.txt/.dtxt`, `prefs.tmp`, `prefsdocs.tmp`, `unisonversion.tex`, directive files, and `../src/strings.ml`.

Dependencies/integration: requires built Unison text binary for preference extraction, OCaml for `docs.ml`, HeVeA, lynx, pdflatex, and make portability features.

Risks: uses GNU group target syntax `&:` with BSD/Solaris compatibility comments; edits must preserve portability. If HeVeA is missing, some targets silently do little, which can leave stale outputs.

Test signals: CI `docs` job runs `opam exec -- make -j 2 docs` and uploads manual text/html/pdf plus generated manpage.
