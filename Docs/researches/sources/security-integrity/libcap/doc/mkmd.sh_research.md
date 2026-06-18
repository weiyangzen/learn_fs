## sources/security-integrity/libcap/doc/mkmd.sh

Purpose: generates markdown versions of libcap manpages plus an index, using Pandoc when available.

Important APIs/functions: `do_page()` converts one manpage or records a redirect; main loop iterates sections 1, 3, 5, 7, and 8; optional `local-md.preamble` and `local-md.postscript` are included.

Control flow: exits successfully without conversion if Pandoc is absent, requires an output directory argument, creates the directory, initializes `index.md`, appends optional preamble, converts each `*.N` page using `pandoc -f man -t markdown`, post-processes bold manpage references into markdown links, writes one `<base>-<section>.md` file per real page, records redirect pages as index links to their targets, and appends more-information text.

State/persistence: creates or overwrites the output directory contents and `index.md`.

Dependencies/integration: Bash, Pandoc, sed, local manpages. Integrates with documentation publishing workflows and `md2html.lua`.

Risks: redirect parsing assumes `.so man` format; sed linkification covers only sections `[1358]` and could miss section 7 or unusual references; generated filenames are based on basename/section and can collide if inputs are unexpected.

Test signals: run `./mkmd.sh md`, inspect `md/index.md`, verify redirect entries, and render with Pandoc plus `md2html.lua`.
