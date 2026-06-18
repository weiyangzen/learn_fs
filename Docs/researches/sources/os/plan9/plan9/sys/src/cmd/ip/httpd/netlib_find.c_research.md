# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/netlib_find.c

Netlib search magic helper invoked from web search forms. It parses `db` and `pat` query fields, chooses a configured searchfs database, mounts it at `/mnt`, writes a `search=` request, and streams matching records as HTML.

Database entries define log labels, maximum hits, backing `/srv/netlib_*` service, record formatter, and page trailer. Formatters preserve plain records, add links for Netlib `file:`/`lib:` fields, and link BibNet URL fields.
