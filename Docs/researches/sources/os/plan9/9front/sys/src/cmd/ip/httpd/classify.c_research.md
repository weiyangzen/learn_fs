# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/classify.c

Country/domain classifier for HTTPD/whois-related filtering. Contains tables of bad countries, good countries, government-domain tokens, and a broad country-code/name list.

`classify` examines ndb tuples for `country`, `dom`, and verified `ip` records. Bad countries always classify as bad, unapproved countries combined with government domains classify as bad government, approved countries classify OK, and missing country evidence returns unknown.

The code treats bad country codes in domain names as meaningful even without forward verification, while country-code inference from domain suffix requires a forward lookup match.
