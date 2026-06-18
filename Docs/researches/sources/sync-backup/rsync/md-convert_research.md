# sources/sync-backup/rsync/md-convert

## Purpose
`md-convert` is a Python 3 documentation generator that converts rsync markdown files into HTML and, for files ending in `.NUM.md`, nroff manpage output. It adds rsync-specific markdown conventions, link-target validation, option-anchor generation, and manpage substitutions.

## Important APIs, Types, and Functions
Top-level functions include `main()`, `parse_md_file()`, `find_man_substitutions()`, `html_via_commonmark()`, `txt2target()`, `manify()`, `htmlify()`, `warn()`, and `die()`. `TransformHtml` subclasses `HTMLParser` and implements `handle_starttag()`, `handle_endtag()`, `handle_data()`, `handle_UE()`, `add_targets()`, and debug output. Important regexes parse filenames, Makefile assignments, version headers, variable references, option dashes, code-target spans, and unsafe anchor characters.

## Control Flow
Argument parsing accepts `--test`, `--dest`, `--force-link-text`, and `--debug`. The script imports `cmarkgfm` first, falling back to `commonmark`; input containing `@USE_GFM_PARSER@` requires cmarkgfm. `parse_md_file()` validates the markdown filename, substitutes version/path variables for manpages, renders markdown to HTML, then feeds the HTML into `TransformHtml`. The parser rewrites HTML while building manpage macros: headings become `.SH`/`.SS`, lists become `.IP`/`.RS`, links become `.UR`/`.UE`, code and emphasis become nroff font escapes, and start-0 ordered lists become description lists. It writes `.html` plus optional extensionless manpage output unless `--test` was requested.

## State and Persistence
Process state includes `env_subs`, parser globals, and `warning_count`. Output files are unlinked before being rewritten. `find_man_substitutions()` reads `version.h`, `Makefile`, git log timestamps, `SOURCE_DATE_EPOCH`, and `RSYNC_OVERRIDE_PREFIX` to produce deterministic manpage headings.

## Dependencies and Integration Points
The script depends on Python 3, `html.parser`, `argparse`, `subprocess`, `cmarkgfm` or `commonmark`, rsync's `version.h`, and the generated `Makefile`. It is invoked by `maybe-make-man` and the build system; `md2man` is a symlink to this same implementation.

## Risks
Link validation is intentionally strict and exits nonzero when warnings are emitted. The HTML-to-manpage transform is stateful and sensitive to parser output shape. Makefile variable expansion assumes referenced variables are already present. The generated anchor scheme must remain stable because documentation links depend on it.

## Test Signals
Tests should run `--test` on a known page, pages requiring GFM, manpage files with substitutions, start-0 description lists, external links with punctuation, duplicate headings, option headings, tables, malformed links, `SOURCE_DATE_EPOCH`, `RSYNC_OVERRIDE_PREFIX`, and warning-to-failure behavior.
