# sources/object-store/openstack-swift/swift/cli/ring_builder_analyzer.py

## Purpose
`ring_builder_analyzer.py` is a developer tool for replaying JSON ring-builder scenarios and measuring rebalance behavior after staged topology changes. It helps quantify ring-builder improvements or regressions by applying scripted add/remove/weight/save commands and printing rebalance convergence metrics per round.

## Important APIs, types, and functions
- `ARG_PARSER` defines `--check` and the scenario file argument.
- `ParseCommandError` decorates validation failures with round and command indexes.
- `_parse_weight()`, `_parse_add_command()`, `_parse_remove_command()`, `_parse_set_weight_command()`, and `_parse_save_command()` validate and normalize scenario commands.
- `parse_scenario(scenario_data)` validates top-level JSON fields (`part_power`, `replicas`, `overload`, `random_seed`, `rounds`) and returns a parsed scenario structure.
- `run_scenario(scenario)` creates a `RingBuilder`, applies each round, repeatedly rebalances with the configured seed, pretends min-part-hours passed between iterations, and prints moved parts, balance, and removed-device counts.
- `main(argv=None)` reads the scenario file, validates it, optionally runs it, and returns a shell status.

## Control flow
Scenario parsing first loads JSON and rejects non-object input. Required numeric fields are type-converted and range-checked: partition power must be 1 through 32, replicas at least 1, overload non-negative, and random seed an integer. Each round must be a list, and each command is dispatched by its first element. Add commands parse Swift ring device strings with `parse_add_value`, default absent regions to 1, default replication IP/port to normal IP/port, and attach a non-negative weight. Remove and set-weight commands parse integer device IDs; save passes a file path through to the builder.

Execution builds `builder.RingBuilder(part_power, replicas, 1)`, applies overload, maps parsed command names to builder methods, and mutates each command list by popping the command name before invocation. After a round, the tool rebalances at least once, advances min-part-hours, then keeps rebalancing until no parts/removed devices change or balance movement is less than one point, except for `MAX_BALANCE` special cases.

## State and persistence behavior
Most state is in-memory `RingBuilder` mutation. The `save` scenario command may persist builder files via `RingBuilder.save`. The scenario list itself is destructively mutated by `run_scenario()` because it pops command names; callers should not reuse the same parsed scenario for repeated runs.

## Dependencies and integration points
The analyzer depends on JSON scenarios, `swift.common.ring.builder.RingBuilder`, `builder.MAX_BALANCE`, and `swift.common.ring.utils.parse_add_value`. It is an offline diagnostic tool rather than a production daemon, but it exercises the same ring-builder algorithms operators use for device changes and rebalances.

## Risks and edge cases
Command validation assumes each command is indexable and non-empty before reading `command[0]`; malformed empty commands can raise a generic exception rather than a `ParseCommandError`. The destructive pop in `run_scenario()` is surprising and makes repeated execution of the same parsed object invalid. The stop condition is heuristic and intended for analysis, not for authoritative ring validation. `save` commands allow scenario files to write paths chosen by the scenario author.

## Test signals
Focused tests should cover JSON validation errors, add parsing defaults, negative weights, unknown commands, empty/malformed command arrays, `--check` behavior, deterministic rebalance output with a seed, `save` dispatch, and whether repeated `run_scenario()` calls on the same object fail due to mutation.
