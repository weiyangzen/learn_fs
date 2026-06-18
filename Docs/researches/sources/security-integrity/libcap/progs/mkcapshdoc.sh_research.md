# sources/security-integrity/libcap/progs/mkcapshdoc.sh

Purpose: generator for `capshdoc.c`.

Important operations: emits C includes and comments, iterates `../doc/values/${x}.txt` in numeric order, derives capability names from `../libcap/cap_names.list.h`, escapes quotes with `sed`, writes `explanationN` arrays, then emits `explanations[]` and `capsh_doc_limit`.

Control flow: sequential numeric loop stops at first missing `values/N.txt`; a second loop emits the pointer table for all generated arrays.

State and dependencies: depends on Bash, grep, sed, doc value files, and cap name list format. It writes to stdout; the Makefile redirects to a `.cf` comparison file.

Risks and test signals: brittle parsing of `cap_names.list.h` and doc file ordering can mislabel docs. The Makefile `diff -u capshdoc.c capshdoc.c.cf` is the explicit guard.
