# File Research: sources/virtualization/open-iscsi/usr/fwparam_ibft/prom_parse.tab.c

Generated GNU Bison 3.0.4 LALR parser implementation for `prom_parse.y`. Most of the file is standard Bison skeleton code: token translation tables, parse stacks, debug printing, error handling, memory growth, location tracking, and the `yyparse(struct ofw_dev *ofwdev)` driver.

The embedded project grammar parses Open Firmware paths and iSCSI OBP parameters into an `ofw_dev`. It recognizes root-only paths, physical bus paths with boot devices, disk labels, OBP qualifiers and parameters, and a virtual-device form. It constructs intermediate strings in fixed-size `STR_LEN` semantic buffers.

Semantic actions set `ofwdev->dev_path` for bus + boot-device paths, deliberately excluding disk labels and OBP parameter suffixes from the stored device path. OBP parameters are handed to helper functions from `iscsi_obp.h`: `obp_parm_hexnum`, `obp_parm_addr`, `obp_parm_iqn`, `obp_parm_str`, and `obp_qual_set`.

The grammar handles IPv4, IPv6-style hex sequences including `::`, optional IPv4 tails, disk partitions, and escaped filenames. It also has debug-only `DPRINT` tracing controlled by `YYDEBUG`.

Operational risks are inherited from the grammar actions: `ofwdev->dev_path` allocations are not checked for `NULL`, and repeated successful parses into the same `ofw_dev` would need ownership discipline outside this file. Direct edits should be avoided; changes belong in `prom_parse.y`.
