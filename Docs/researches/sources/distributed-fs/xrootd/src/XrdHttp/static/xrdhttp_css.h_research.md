# sources/distributed-fs/xrootd/src/XrdHttp/static/xrdhttp_css.h

Purpose: Embeds the XrdHTTP directory/listing stylesheet as a C byte array.

Important APIs/types/functions: Defines `unsigned char static_css_xrdhttp_css[]` and `unsigned int static_css_xrdhttp_css_len`. The bytes decode to CSS for HTML/body defaults, links, header, file table columns/classes, file/folder icons, link coloring, metadata links, footer, and request-by text.

Control flow: No executable control flow. The HTTP static resource path serves the byte array with the recorded length.

State and persistence: Static compiled asset data only. No mutation or durable state.

Dependencies and integration points: Included by `XrdHttpStatic.hh` and consumed by static response serving code. The original CSS likely lives beside it as `xrdhttp.css`.

Risks: Global definitions in a header can duplicate symbols if included from multiple translation units. Regeneration must keep symbol names and length accurate. The CSS references `/icons/generic.gif` and `/icons/folder.gif`, so serving those paths affects visual completeness.

Test signals: Verify served CSS byte length equals `static_css_xrdhttp_css_len`, content type is correct, directory listing uses the expected styles, and no duplicate-symbol link failures occur.
