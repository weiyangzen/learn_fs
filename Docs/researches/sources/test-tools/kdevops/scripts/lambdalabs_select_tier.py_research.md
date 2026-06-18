# sources/test-tools/kdevops/scripts/lambdalabs_select_tier.py

## Purpose
`lambdalabs_select_tier.py` selects the highest available Lambda Labs GPU instance from predefined performance fallback tiers, supporting single-GPU and 8-GPU groups.

## Important APIs, Types, And Functions
Important data structures are `GPU_TIERS_1X`, `TIER_ORDER_1X`, `GPU_TIERS_8X`, `TIER_ORDER_8X`, `TIER_GROUPS_1X`, `TIER_GROUPS_8X`, and combined `TIER_GROUPS`. Functions are `get_capacity_map()`, `check_instance_availability()`, `select_instance_from_tiers()`, `list_tier_groups()`, and `main()`.

## Control Flow
`select_instance_from_tiers()` validates the tier group, loads an API key, fetches the capacity map, optionally prints available GPU capacity, chooses the correct tier table based on `8x-` prefix, then walks tiers from highest to lowest and returns the first instance type with any region. `main()` either lists tiers or prints `instance_type region` for the selected result.

## State And Persistence
No persistence. Exit status indicates whether a tier selection was found.

## Dependencies And Integration Points
Depends on `lambdalabs_api.py`, `argparse`, `json`, `os`, `sys`, and typing. Integrates with provisioning scripts that can accept a selected instance and region pair from stdout.

## Risks And Edge Cases
Tier instance names are hardcoded and must match Lambda Labs API names. The first region in API order is chosen without latency/cost preference. Verbose output contains Unicode check/cross marks. No API key or no matching capacity returns failure with minimal machine-readable detail.

## Test Signals
Mock capacity maps for each tier group, unavailable high tiers with fallback, unknown group, missing API key, `--list-tiers`, verbose output, and 8x group selection.
