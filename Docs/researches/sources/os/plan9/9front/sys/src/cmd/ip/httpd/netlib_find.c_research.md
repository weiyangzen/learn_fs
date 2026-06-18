# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/netlib_find.c

Magic helper invoked from Netlib search forms. It parses `db` and `pat` query fields, mounts the selected searchfs database from `/srv/netlib_*` at `/mnt`, writes a `search=` request, then streams matching records as HTML.

The database table controls log labels, maximum hits, backing service, record formatter, and page trailer. Formatters preserve plain records, turn Netlib `file:`/`lib:` fields into links, and link BibNet `URL` fields. HEAD requests return headers and no body.
