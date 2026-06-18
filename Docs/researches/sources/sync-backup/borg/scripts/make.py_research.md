# sources/sync-backup/borg/scripts/make.py

Purpose: Provides developer build helpers for generated usage documentation, man pages, and cleanup of generated C/compiled Cython artifacts.

Important APIs/types/functions: Top-level helper `format_metavar(option)` formats argparse nargs. `BuildUsage` has `run`, `generate_level`, `write_usage`, `write_options`, `rows_to_table`, and `write_options_group`. `BuildMan` has `run`, `generate_level`, `build_topic_pages`, `build_intro_page`, `new_doc`, `printer`, `write_heading`, `write_man_header`, `write_examples`, `write_see_also`, `gen_man_page`, `write_usage`, `write_options`, and `write_options_group`. `Clean.run` removes generated `.c` and compiled extension artifacts for `cython_sources`. `main(argv)` dispatches `clean`, `build_usage`, and `build_man`.

Control flow: `build_usage` imports Borg, sets `borg.doc_mode = "build_man"`, builds the `Archiver` parser, recursively finds subcommands, skips debug commands, and emits `docs/usage/<command>.rst.inc` plus `common-options.rst.inc`. `build_man` builds man pages for commands, help topics, borgfs, and the intro page, extracts examples from usage pages, registers docutils roles, and writes `docs/man/*.1`.

State and persistence: Writes generated docs under `docs/usage/` and `docs/man/`; `Clean` deletes generated C and compiled extension files. The man header date uses `SOURCE_DATE_EPOCH` when set for reproducibility.

Dependencies and integration points: Depends on Borg parser internals (`Archiver.build_parser`, `SubCommands` action class naming, parser epilog/description), docutils manpage writer, Sphinx/rST conventions, and `borg.archiver._common.rst_plain_text_references`. It is the generator responsible for the usage `.rst.inc` files researched in this work item.

Risks: It uses private argparse/parser structures (`_actions`, `_action_groups`) and class-name string matching, so parser refactors can break docs generation. `rows_to_table` computes table widths from raw strings, making very long help text produce wide rST tables. `write_examples` relies on include ordering in `docs/usage/*.rst`.

Test signals: Run `python scripts/make.py build_usage`, `python scripts/make.py build_man`, and `tox -e docs`. Diff generated includes/man pages after parser changes. Test `clean` on generated C/compiled artifacts without deleting source `.pyx`.
