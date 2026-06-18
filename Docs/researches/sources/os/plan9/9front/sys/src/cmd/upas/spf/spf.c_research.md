# File Research: sources/os/plan9/9front/sys/src/cmd/upas/spf/spf.c

`spf.c` is a standalone SPF evaluator. It fetches SPF records from TXT/SPF DNS records or `-t`, parses mechanisms/modifiers into a flat `spftab`, recursively expands `include`/`redirect`, performs A/MX/PTR/exists/IP4/IP6 lookups, applies macro expansion, supports CIDR matching, and walks the resulting mechanism list against an IP.

The result is expressed through exit status: with sender/IP arguments it exits `fail` on SPF failure; with only a domain it prints records by default. Flags control debug, strict end failure, no macro expansion, print, recursion tracing, netroot, and verbose matching.

Notable caveats are called out in comments: query/recursion limits are pragmatic, `exists` and PTR behavior are ad hoc, and root-domain fallback is heuristic for several ccTLDs.
