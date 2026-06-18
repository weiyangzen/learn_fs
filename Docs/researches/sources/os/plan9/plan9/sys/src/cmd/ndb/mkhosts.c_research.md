# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/mkhosts.c

Generates legacy host/DNS export files for a selected domain from NDB sources. Default domain is `research.att.com`; default input files are `/lib/ndb/local` and `/lib/ndb/friends`.

`parse()` reads NDB entries with IP data, skips console-flavored entries, keeps only entries in the selected domain or with `ipnet`, and records each IP tuple in a fixed global array. Output functions generate DNS-style A/CNAME/MX records, equivalence domain lists, and text host/net records.

`main()` writes `/lib/ndb/db.<domain>`, `/lib/ndb/equiv.<domain>`, and `/lib/ndb/txt.<domain>`, with a generated-file warning in the DB output. Some old hosts-file output is commented out.

Risks include fixed `x[4096]`, in-place uppercasing of tuple values, domain-specific formatting width assumptions, and hard-coded `/lib/ndb` output paths.
