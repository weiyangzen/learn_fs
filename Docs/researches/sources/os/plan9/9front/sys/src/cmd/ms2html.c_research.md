# File Research: sources/os/plan9/9front/sys/src/cmd/ms2html.c

Converts troff/ms-style input to HTML. It includes a compact macro processor, escape translator, conditional evaluator, include stack, and HTML emitter.

Key responsibilities:
- Defines supported ms/troff directives and dispatch tables for macros, pseudo-ops, conditionals, strings, and raw HTML helpers.
- Maintains global rendering state for title, basename, equation delimiter, indentation, lists, examples, headings, author blocks, anchors, conditionals, and font stack.
- Provides large entity and troff-special-character translation tables for HTML output.
- Implements string registers, number registers, macro definitions/appending/removal, macro argument substitution, and nesting stacks for strings/macros/includes.
- Reads logical runes from stdin, included files, macro bodies, or string expansions, with escape expansion in `getnext`.
- Handles troff escapes for strings, macro args, special chars, font changes, number registers, size changes, vertical movement, horizontal rules, comments, line continuation, superscript/subscript, and HTML escaping.
- Parses directives and arguments, including quoted/null arguments.
- Emits an HTML document with title/body setup and closing cleanup.
- Implements common ms macros: paragraphs, lists, indents, headings, numbered headings, title, authors, font macros, displays/preformatted blocks, abstracts, footnotes, quotes, references, raw HTML/title injection, and Bell Labs address macros.
- Handles `.EQ`, `.TS`, and `.PS` blocks by piping content through `troff2gif` and embedding generated GIFs.
- Handles `.BP` picture conversion through `ps2gif` unless the input already looks like JPEG/GIF.
- Implements `.if`, `.ie`, `.el`, arithmetic/condition evaluation, braced body push/skip, `.ds`, `.as`, `.ig`, `.so`, `.lf`, and Web reference helpers.

Important interactions:
- Uses Plan 9 `Biobuf`, process/fork calls, `troff2gif`, `ps2gif`, and image file side effects for generated auxiliary GIFs.
- The `-b`, `-d`, `-q`, and `-t` options control auxiliary image basename, equation delimiters, quiet logging, and title.

Notable quirks:
- The generated HTML is old-style and intentionally simple.
- Many ms/troff macros are ignored or approximated.
- Include and macro/string nesting are bounded by fixed constants.
