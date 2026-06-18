# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/altq.c

ALTQ integration support for the FreeBSD `ipfw` command through PF control ioctls.

Key behavior:
- `altq_set_enabled()` opens `/dev/pf` and starts/stops ALTQ with `DIOCSTARTALTQ` or `DIOCSTOPALTQ`.
- `altq_fetch()` lazily reads the PF ALTQ queue list with `DIOCGETALTQS`/`DIOCGETALTQ` and caches queue entries in a TAILQ.
- `altq_name_to_qid()` maps a queue name to PF ALTQ qid for rule parsing.
- `print_altq_cmd()` maps a qid back to a queue name when printing ipfw rules.

Research notes:
- Requires PF support and `PFIOC_USE_LATEST`.
- Missing queue names are fatal during name-to-qid parsing but print as `?<qid>` during reverse lookup.
