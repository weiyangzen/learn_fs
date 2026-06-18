# File Research: sources/os/bsd/openbsd-src/sbin/ipsecctl/Makefile

This OpenBSD makefile builds `ipsecctl`.

Key contents:
- `PROG= ipsecctl`
- Man pages: `ipsecctl.8` and `ipsec.conf.5`
- Sources:
  - `ike.c`
  - `ipsecctl.c`
  - `pfkey.c`
  - `pfkdump.c`
  - `parse.y`
- Adds include path for the current directory.
- Enables warning flags including strict prototypes, missing prototypes/declarations, shadowing, pointer arithmetic, cast-qual, and sign-compare.
- Includes `<bsd.prog.mk>`.

Relevance:
- The source list shows this batch includes the command front-end and IKE config generator but not the PF_KEY backend/parser files in this work item.
