# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpStatic.hh

Purpose: Central include for small compiled-in HTTP static assets used by the XrdHTTP directory/listing UI.

Important APIs/types/functions: No functions or classes. Includes `static/xrdhttp_css.h` and `static/xrdhttp_favicon_ico.h`; a logo include is present but commented out.

Control flow: Consumers include this header to get the asset arrays and lengths in translation units that serve static resources.

State and persistence: Asset bytes are compiled into process memory. No runtime mutation or persistence occurs.

Dependencies and integration points: Depends on generated C headers produced from static resources, likely by a binary-to-C tool. Integrates with the XrdHTTP static file serving path.

Risks: Included headers define global arrays rather than `extern` declarations, so multiple inclusion across translation units can cause duplicate symbol/link issues unless only included in controlled places. Asset regeneration must preserve symbol names.

Test signals: Build/link with all consumers, request CSS and favicon resources, and verify lengths match served payload bytes.
