# File Research: sources/os/plan9/plan9/sys/src/cmd/wikifs/wiki.h

This header defines the shared wiki data model and function contracts.

Limits:
- `Tcache`: cache freshness window.
- `Maxmap`: maximum map file size.
- `Maxfile`: maximum page write size.

Wiki node types:
- Paragraph marker, heading, bullet, link, man reference, plain text, preformatted text, horizontal rule.

Structures:
- `Wpage`: linked parsed markup node with type, text, man section, optional URL, and next pointer.
- `Whist`: refcounted page history with page number, title, doc array, count, and current index.
- `Wdoc`: one version with author, comment, conflict flag, timestamp, and parsed page.
- `Sub`: template substitution pair.
- `Mapel`: title-to-number entry.
- `Map`: refcounted title map with entries, timestamp, raw buffer, and qid.

Declared APIs:
- Allocation/string helpers.
- Parser/history readers.
- HTML/text conversion.
- Cache/map/page I/O: current/history lookup, page write, cache invalidation, allocation, title lookup.
- Map close/current functions.
- Wikidir-relative file wrappers.

Globals:
- `map`, `maplock`, `wikidir`.

Role:
- Shared interface across all wikifs implementation and utility files.
