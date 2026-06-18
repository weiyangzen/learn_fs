# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/classify.c

Domain/country classifier for whois or access-policy code. It defines country-code/name tables for blocked countries, accepted countries, government labels, and all known country codes.

`classify` inspects NDB tuples for `country`, `dom`, and verified `ip` entries. It returns unknown, bad-country, bad-government, or OK classifications based on explicit country data, domain suffixes, government domain components, and forward-lookup verification.
