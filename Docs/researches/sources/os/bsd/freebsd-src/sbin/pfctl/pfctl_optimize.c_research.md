# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/pfctl_optimize.c

## Purpose

`pfctl_optimize.c` implements pfctl’s filter-rule optimizer. It rewrites parsed filter rules before kernel load while preserving rule semantics. Its major goals are:
- Remove duplicate or fully shadowed rules.
- Combine similar rules into PF tables when enough addresses are present.
- Reorder rules inside safe semantic blocks to improve kernel skip-step behavior.
- Optionally use live rule counters to reorder `quick` rules by observed traffic.

## Core Concepts

### Superblocks

A `superblock` is a contiguous list of rules with compatible semantics. Rules inside a superblock may be reordered or combined without changing observable policy. Rules that cannot safely move become barriers or force a new block.

Each superblock contains:
- `sb_rules`: optimized rule list.
- `sb_profiled_block`: matched current-kernel rule block for profile-guided optimization.
- `sb_skipsteps[PF_SKIP_COUNT]`: skip-step grouping lists.

### pf_skip_step

`struct pf_skip_step` groups rules sharing a field used by PF skip steps, such as interface, direction, address family, protocol, source/destination address, or source/destination port. Reordering tries to put common groups adjacent.

### Rule Field Descriptor

`pf_rule_desc[]` classifies fields in `struct pfctl_rule`:
- `BARRIER`: nonzero field forces the rule into its own block.
- `BREAK`: field must match within a superblock.
- `NOMERGE`: may reorder but cannot differ for table-combine merging.
- `COMBINED`: field may be merged into generated tables.
- `DC`: ignored for comparisons, generally kernel counters or derived fields.
- `NEVER`: should not be set in pass/block rules.

Fields such as labels, probability, max states, source limits, and anchors are barriers. Action, logging, quickness, tags, queueing, NAT/RDR/route pools, and similar behavior-affecting fields are breaks.

## Main Optimization Flow

`pfctl_optimize_ruleset()`:
1. Returns immediately for an empty filter ruleset.
2. Initializes skip comparators and table generation state.
3. Moves active rules into the inactive list.
4. Copies each rule into `struct pf_opt_rule`, preserving pool lists.
5. Partitions the flat queue into superblocks with `construct_superblocks()`.
6. Optionally loads feedback profile data when `PF_OPTIMIZE_PROFILE` is enabled.
7. Optimizes each superblock with `optimize_superblock()`.
8. Rebuilds the active filter ruleset with new rule numbers.
9. Releases table references and temporary optimizer state.

On errors it frees outstanding optimizer queues and superblocks.

## Optimization Passes

`optimize_superblock()` runs passes in this order:
1. `remove_identical_rules()`
2. `combine_rules()`
3. profile-guided `block_feedback()` for quick rules when available, otherwise `reorder_rules()`

The comment explicitly says no passes should be added after `reorder_rules()` because it can split a superblock into smaller blocks.

## Duplicate And Superset Removal

`remove_identical_rules()` compares each pair of rules after:
- Reducing them with `comparable_rule(..., DC)`.
- Applying `exclude_supersets()` in both directions.

If one rule is identical to or covered by another, it removes the redundant rule.

`exclude_supersets()` normalizes a sub-rule when a super-rule has broader fields:
- Empty interface matches all interfaces.
- `PF_INOUT` covers direction.
- Protocol zero covers any protocol.
- Empty port operator covers ports.
- Zero netmask covers all source/destination addresses.
- Broader CIDR masks can cover narrower CIDR addresses.
- Address family zero covers any family.

## Combining Rules Into Tables

`combine_rules()` searches for rules that differ only in source or destination address and whose differing addresses can become table members.

Requirements:
- Table loading must be enabled in `pf->loadopt`.
- Only one side may differ at a time.
- The different address must be `PF_ADDR_ADDRMASK`.
- Port operators, port values, negation, and other non-combinable fields must match.
- `rules_combineable()` must succeed.

`TABLE_THRESHOLD` is 6. Before reaching the threshold, related rules keep references to the candidate table. Once the threshold is reached:
- A generated const table is created.
- One remaining rule is rewritten to reference that table.
- Duplicate covered rules are removed.
- Verbose mode prints the generated table definition.

`add_opt_table()` creates temporary optimizer tables and appends host nodes.

`pf_opt_create_table()` picks a collision-resistant generated table name using an `arc4random()` identifier and current global table list, then calls `pfctl_define_table()`.

## Reordering For Skip Steps

`reorder_rules()`:
1. Builds skip-step grouping lists for each comparator.
2. Ignores fields that either match all rules or match only one rule.
3. Finds the largest useful grouping.
4. Moves matching rules adjacent.
5. If the group is large enough, splits it into a new superblock and recurses.
6. Leaves unmatched rules in original order when no useful commonality remains.

Skip comparators:
- `skip_cmp_ifp`
- `skip_cmp_dir`
- `skip_cmp_af`
- `skip_cmp_proto`
- `skip_cmp_src_addr`
- `skip_cmp_dst_addr`
- `skip_cmp_src_port`
- `skip_cmp_dst_port`

`skip_init()` maps PF skip constants to comparator functions.

`remove_from_skipsteps()` maintains the skip-step lists after a rule is extracted.

## Profile-Guided Optimization

`load_feedback_profile()` fetches currently loaded pass rules from the kernel and partitions them into profiled superblocks. It tries to align current-kernel superblocks with the new superblocks using `BREAK`-level comparable rules.

`block_feedback()` copies packet counters from matching profiled rules to new rules, then sorts rules in descending profile count. This pass is only applied to suitable `quick` superblocks.

## Superblock Construction

`construct_superblocks()` walks the optimizer queue and starts a new superblock when `superblock_inclusive()` rejects the next rule.

`superblock_inclusive()` rejects inclusion when:
- A barrier field is nonzero.
- Per-rule source tracking is enabled.
- Interface groups differ in a way that could change runtime semantics.
- `NOMERGE`-level comparable rules differ from the first rule in the block.

The interface-group logic is intentionally conservative because group membership can change at runtime.

`interface_group()` uses `SIOCGIFGMEMB` to determine whether an interface name is a group.

## Comparison And Table Helpers

- `addrs_equal()` compares PF rule address wrappers.
- `addrs_combineable()` checks table-combine eligibility.
- `rules_combineable()` compares rules with `COMBINED` fields zeroed.
- `comparable_rule()` copies a rule and zeroes fields at or above a requested descriptor class.
- `pf_opt_table_ref()` / `pf_opt_table_unref()` manage optimizer table reference counts.

## Memory Management

The optimizer copies parsed rules into temporary `pf_opt_rule` nodes, moves pool lists carefully, and frees temporary tables through reference counting. `superblock_free()` recursively frees superblocks, profiled blocks, rule wrappers, and table references.

## Role In This Group

This file is a compact example of conservative source-to-source policy optimization. It balances performance improvements against the risk of changing firewall behavior by enforcing explicit semantic barriers and only transforming rules inside compatible contiguous blocks.
