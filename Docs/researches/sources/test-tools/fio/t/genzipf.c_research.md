# sources/test-tools/fio/t/genzipf.c

## Purpose
Generates and summarizes synthetic Zipf, Pareto, or normal access distributions using fio's distribution libraries, helping users choose fio random distribution parameters and cache-size expectations.

## Important APIs, Types, and Functions
`struct node` records a unique generated offset and hit count. Hash helpers `hashv()`, `hash_lookup()`, and `hash_insert()` track unique offsets in a chained hash table. `parse_options()` configures type, input parameter, GiB size, block size, output rows, cache-hit percentage, and CSV mode. `output_csv()` and `output_normal()` render ranked hit counts and bucket summaries.

## Control Flow
`main()` parses options, computes the number of block ranges, initializes the selected fio distribution state (`zipf_init`, `pareto_init`, or `gauss_init`), builds a hash sized from range count, samples one value per range, increments unique-node hit counters, sorts nodes by hit count, and outputs either CSV or a human summary.

## State and Persistence Behavior
All state is transient heap memory. Output is stdout. The optional `-p` percentage reports how much cache would satisfy the requested percentage of hits.

## Dependencies and Integration Points
Uses fio's `zipf`, `gauss`, list, and Jenkins hash helpers. The results map directly to fio distribution configuration values and block-size/data-set sizing decisions.

## Risks
Memory use scales with `nranges`; the default 500 GiB at 4 KiB implies a very large `nodes` allocation and hash table. `int` loop counters over `nranges` can overflow on large data sets. Default `dist_val` for normal distribution remains zero unless supplied. Input validation is minimal for zero block size and huge row counts.

## Test Signals
Useful tests include small deterministic data sets for each distribution, CSV format validation, invalid distribution parameter rejection, and cache-percentage output sanity.
