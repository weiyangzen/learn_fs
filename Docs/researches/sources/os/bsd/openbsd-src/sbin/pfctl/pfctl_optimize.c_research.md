# File Research: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_optimize.c

`pfctl_optimize.c` implements conservative userland rule optimization before rules are loaded into the kernel. It groups compatible adjacent rules into superblocks, removes duplicates/subsets, combines many address-differing rules into generated PF tables, reorders rules to improve kernel skip-step behavior, and optionally uses current kernel rule counters as a profile to prioritize quick rules.

Primary responsibilities:
- Defines optimization metadata for `struct pf_rule` fields via `pf_rule_desc[]`, classifying fields as `BARRIER`, `BREAK`, `NOMERGE`, `COMBINED`, `DC`, or `NEVER`.
- Defines `struct superblock`, a sequence of adjacent semantically compatible rules that may be optimized internally.
- Defines `struct pf_skip_step`, per-skip-dimension groups used to find common fields for skip-step-friendly ordering.
- Implements `pfctl_optimize_ruleset()` as the top-level transform from `struct pf_rule` queue to optimized rule queue.
- Creates optimizer-generated const tables when enough similar rules differ only by source or destination address.

Optimization pipeline:
- `construct_superblocks()` partitions the ruleset into superblocks using `superblock_inclusive()`.
- `remove_identical_rules()` removes exact duplicate or covered rules after normalizing don't-care fields and supersets.
- `combine_rules()` detects rules that differ only by source or destination address and builds an optimizer table once the rule count reaches `TABLE_THRESHOLD` (6).
- `reorder_rules()` builds skip-step lists for interface, direction, rdomain, AF, protocol, source/destination address, and source/destination port, then reorders or recursively splits blocks to maximize common skip jumps.
- `load_feedback_profile()` fetches the active kernel ruleset, constructs comparable superblocks, and attaches matching profile blocks.
- `block_feedback()` orders quick rules by observed packet counts from the active ruleset when profile optimization is requested.

Generated table flow:
- `add_opt_table()` creates a temporary `pf_opt_tbl`, appends addresses with `append_addr_host()`, and stores printable nodes for verbose output.
- `pf_opt_create_table()` snapshots existing tables, chooses a collision-resistant name using `PF_OPTIMIZER_TABLE_PFX`, `arc4random()`, and a counter, then calls `pfctl_define_table()`.
- Once a table is generated, the rule address is rewritten to `PF_ADDR_TABLE` and the generated table name is copied into the rule.

Semantic safety:
- `BARRIER` fields force a rule into its own block and prevent reordering.
- `BREAK` fields must be equal across a superblock.
- `NOMERGE` fields may allow reordering but prevent rule combination.
- `COMBINED` fields are the only address fields that can be replaced by generated tables.
- Interface groups are treated as superblock breaks when names differ, because group membership can change at runtime and could invalidate reordering assumptions.
- Per-rule source tracking (`PFRULE_RULESRCTRACK`) also forces a hard break.

Integration points:
- Called by `pfctl_load_ruleset()` in `pfctl.c` when optimization is enabled.
- Uses parser structures from `pfctl_parser.h`: `pf_opt_rule`, `pf_opt_tbl`, node initializers, and table helpers.
- Uses address/table helpers from `pfctl_parser.c` and `pfctl_radix.c`: `append_addr_host()`, `unmask()`, `pfr_get_tables()`, `pfctl_define_table()`, and `print_tabledef()`.
- Reads live kernel rules via `DIOCGETRULES`/`DIOCGETRULE` for profile optimization.

Notable risks and edge cases:
- The optimizer intentionally avoids many possible optimizations to preserve PF semantics; labels, anchors, probability, max-state fields, and several state/queue/route attributes block movement.
- Table generation only combines address masks, not ports or mixed v4/v6 rules.
- Several internal TODO comments call out possible improvements and protocol-specific skip-step nuances.
- Memory ownership is mostly process-lifetime oriented; table refs are reference-counted, but optimization exits soon after load.
