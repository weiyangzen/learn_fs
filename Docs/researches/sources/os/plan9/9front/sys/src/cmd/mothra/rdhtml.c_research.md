# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/rdhtml.c

Implements Mothra’s plain-text and HTML reader/rendering pipeline. It tokenizes input, maintains a small formatting stack, extracts titles/anchors/links/images/forms, and emits `Rtext` nodes for display by the panel text view.

Key responsibilities:
- Loads and caches four font families/sizes through `pl_whichfont` and `getfonts`.
- Maintains HTML parse state with stack push/pop helpers that duplicate/free inherited link, image, and anchor state.
- Reads input through buffered routines that normalize line endings, decode UTF-8 runes, and provide putback.
- Tokenizes permissive HTML: start/end tags, comments, script/style content, preformatted text, entity references, attributes, and normal text.
- Parses attributes case-insensitively and supports quoted/unquoted values, entity removal, and limited error reporting through `htmlerror`.
- Emits text with font, indentation, line break, paragraph, vertical offset, hot-link, strike-through, and attached `Action` metadata.
- Handles plain text by preserving line breaks, tabs, and fixed-width font rendering.
- Implements broad tag behavior for headings, lists, blockquotes, links, anchors, images, base URL, meta refresh, media/frame fallback links, tables, preformatted regions, title, inline styles, forms, and script/style suppression.
- Auto-linkifies obvious `http://`, `https://`, `gemini://`, `ftp://`, and some `www.` tokens.
- Starts image retrieval with `getpix` after EOF unless image loading is disabled.

Important interactions:
- Uses `html.h` tag/action metadata and `rtext.h` output primitives.
- Delegates form tags to `rdform`, `endform`, and field panel creation elsewhere.
- Calls `urlresolve` for `<base href=...>` and stores output in the current page’s `Www`.
- Sets `dst->changed` as output grows and calls `finish(dst)` when parsing is complete.

Notable quirks:
- Parsing is intentionally tolerant and incomplete; many tags are simplified or reported as unimplemented/deprecated.
- Script/style bodies are skipped as display text, not executed.
- Some modern media tags are represented as bracketed links rather than rendered media.
