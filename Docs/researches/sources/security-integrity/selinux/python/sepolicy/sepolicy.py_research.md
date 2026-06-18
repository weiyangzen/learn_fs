# sources/security-integrity/selinux/python/sepolicy/sepolicy.py

## Purpose
This is the executable `sepolicy` CLI and compatibility entry point for `sepolgen`. It exposes policy inspection, generation, manpage creation, network queries, boolean descriptions, interface listing, transition analysis, communication analysis, and a GUI launcher through argparse subcommands.

## Important APIs, Classes, And Functions
Validation actions subclass `argparse.Action`: `CheckPath`, `CheckType`, `CheckBoolean`, `CheckDomain`, `CheckClass`, `CheckAdmin`, `CheckPort`, `CheckPortType`, `LoadPolicy`, `CheckUser`, `CheckRole`, and `InterfaceInfo`. These convert or validate CLI arguments against live policy data and store normalized values on the argparse namespace.

Command handlers include `network()`, `gui_run()`, `manpage()`, `communicate()`, `booleans()`, `transition()`, `interface()`, and `generate()`. Each has a corresponding `gen_*_args()` function that registers parser arguments. Utility functions include `generate_custom_usage()`, `port_string_to_num()`, `_print_net()`, `manpage_work()`, and `print_interfaces()`.

The `__main__` block creates the top-level parser, registers all subcommands, supports `-P/--policy` via `LoadPolicy`, rewrites invocation as `sepolgen` to `generate`, parses arguments, calls `args.func(args)`, and maps `ValueError`, `IOError`, and `KeyboardInterrupt` to process exits.

## Control Flow
Startup imports SELinux and sepolicy modules, installs gettext fallback `_`, and defines custom usage for `sepolicy generate`. Argument generation builds subparsers for booleans, communicate, generate, gui, interface, manpage, network, and transition.

`network()` builds port dictionaries, handles mutually exclusive list/port/type/domain/application queries, resolves application init transition types into domains, and prints bind/connect permissions through `_print_net()`. `manpage()` optionally loads an alternate-root policy, selects all or requested domains, uses a multiprocessing pool with fork start method to run `manpage_work()`, and optionally emits HTML index pages. `generate()` validates policy type combinations, derives a name from application command when needed, configures a `sepolicy.generate.policy` object, adds write paths/domains/users/admin roles, and prints generated output paths.

`interface()` lists admin, user-role, all, or selected interfaces and can print verbose formatted information or run compile tests. `communicate()`, `booleans()`, and `transition()` are thinner wrappers around sepolicy library calls.

## State And Persistence
The script mutates process policy state when `LoadPolicy` calls `sepolicy.policy(values)` and when `manpage()` loads an alternate-root policy. `generate()` writes policy template files through the `sepolicy.generate.policy.generate()` call. `manpage()` writes man pages and optional HTML to `args.path`. `gui_run()` opens GUI state externally. Global `all_classes` caches class names after first validation.

## Dependencies And Integration Points
It depends on the Python `selinux` binding, the `sepolicy` Python package, optional submodules `sepolicy.gui`, `sepolicy.manpage`, `sepolicy.network`, `sepolicy.communicate`, `sepolicy.transition`, `sepolicy.interface`, and `sepolicy.generate`, plus multiprocessing. It integrates with installed SELinux policy, `/sys/fs/selinux/policy` by default, alternate policy files, generated manpage content, and the Makefile-installed `sepolicy`/`sepolgen` entry points.

## Risks And Edge Cases
Several argparse actions raise `ValueError` rather than `argparse.ArgumentError`, so errors are caught only after top-level parse handling and may produce less standard argparse output. `CheckPort` allows values up to `65536`, although valid TCP/UDP ports normally end at `65535`. `CheckRole` strips the final two characters from a role value, assuming a `_r` suffix without validating that suffix. `generate()` defines command policy types with `--init` defaulting `policytype` to daemon, which means default interactions around omitted policy types require careful testing.

`manpage()` unconditionally calls `multiprocessing.set_start_method('fork')`, which can raise if a start method was already set in an embedding process. Multiprocessing propagates worker exceptions only when `result.get()` is called. Many commands depend on live SELinux policy data and optional packages, so behavior is environment-sensitive.

## Test Signals
This subset does not include `test_sepolicy.py`; the Makefile refers to it as the main test target. Indirect validation should cover parser setup for every subcommand, argument validation against mocked or fixture policy data, generated policy output paths, manpage parallelism, network formatting, and `sepolgen` symlink invocation behavior.
