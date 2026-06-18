<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/scripts/datacrunch_select_tier.py -->
# sources/test-tools/kdevops/scripts/datacrunch_select_tier.py

Purpose: selects the best available DataCrunch GPU instance from named fallback tier groups such as `h100-or-less` or `b300-or-less`. It is designed for automation that can accept progressively lower GPU tiers when higher tiers have no capacity.

Important APIs and data: `GPU_TIERS` maps tier names to DataCrunch instance type strings; `TIER_ORDER` orders tiers from highest to lowest; `TIER_GROUPS` defines common maximum-tier groups. `get_all_available_capacity()` shells out to `datacrunch_check_capacity.py --json`; `check_instance_availability()` scans a capacity map; `check_instance_on_demand()` invokes the capacity checker for a specific on-demand instance; `select_instance_from_tiers()` implements fallback; `list_tier_groups()` prints available groups; `main()` returns `instance_type location`.

Control flow: the CLI lists tiers or validates a requested group, fetches capacity once, iterates tiers in priority order, skips excluded instance types, checks spot first, optionally probes on-demand, and exits 0 on a selection.

State and persistence: no persistent writes; it reads credentials indirectly through the capacity checker and emits the selected pair on stdout.

Dependencies and integration: depends on Python subprocess and JSON plus sibling `datacrunch_check_capacity.py`. Terraform bringup playbooks invoke it for wildcard tier selections and retry exclusions.

Risks: all capacity failures collapse to an empty map, making auth/network/schema errors indistinguishable from no capacity unless verbose output catches context. Tier definitions are hardcoded and can drift from provider inventory. Test signals include monkeypatching `subprocess.run`, tier ordering tests, exclusion handling, on-demand fallback behavior, and CLI exit codes.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/scripts/datacrunch_select_tier.py -->
