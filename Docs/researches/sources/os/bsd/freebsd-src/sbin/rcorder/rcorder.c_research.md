# File Research: sources/os/bsd/freebsd-src/sbin/rcorder/rcorder.c

Dependency sorter for rc-style scripts.

Key elements:
- Parses options `-d`, `-g`, `-k keyword`, `-p`, and `-s keyword`.
- `crunch_file` reads regular files using `fparseln`, scans initial dependency comment block, and records `# REQUIRE:`, `# REQUIRES:`, `# PROVIDE:`, `# PROVIDES:`, `# BEFORE:`, `# KEYWORD:`, and `# KEYWORDS:`.
- `add_provide` maps provision names to provider lists in `provide_hash`; duplicate providers are allowed.
- `add_before` stores `BEFORE` constraints, and `insert_before` converts each into a fake provision required by files that provide the target.
- `satisfy_req` recursively satisfies requirement providers, detects missing providers and circular provision dependencies, and emits Graphviz edges when requested.
- `do_file` recursively processes requirements, assigns sequence numbers, removes satisfied providers from provision lists, tracks circular-dependency issues, and queues printable files if keyword filters allow.
- `generate_ordering` drives the traversal, sorts by sequence, and prints one file per line or same-sequence files on one line with `-p`.
- Graphviz mode emits provider nodes, dependency edges, missing-provider nodes, and red highlighting for cycle participants.

Dependencies:
- Uses `libutil` `fparseln`, `basename`, local `ealloc`, `sprite`, and `hash` infrastructure.

Research notes:
- Keyword filters are post-ordering output filters: `-s` suppresses matching files, `-k` keeps only matching files unless no keep list exists.
- Fake provision names are prefixed `fake_prov_` and hidden from normal Graphviz edge labels.
- Circular dependency handling continues after warnings and pushes involved files toward the tail by sequence.
