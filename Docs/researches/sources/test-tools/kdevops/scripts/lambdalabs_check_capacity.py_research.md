# sources/test-tools/kdevops/scripts/lambdalabs_check_capacity.py

## Purpose
`lambdalabs_check_capacity.py` reports Lambda Labs GPU instance capacity across regions, checks a specific instance type, and can print the first available region for scripting.

## Important APIs, Types, And Functions
Functions are `_build_region_map()`, `check_availability(instance_type=None, json_output=False, pick_first=False)`, and `main()`. CLI options are `--instance-type/-i`, `--json/-j`, and `--pick-first`.

## Control Flow
The script loads an API key, fetches `capacity_map` via `get_instance_types_with_capacity()`, and either handles a specific instance type or all GPU instances. Specific checks print a first region, JSON, or human text and return 0 only when capacity exists. Global checks filter `gpu_` instance types with non-empty regions, optionally emit JSON grouped by region, or print a human region list.

## State And Persistence
No state is written. Exit status is meaningful for automation.

## Dependencies And Integration Points
Depends on `lambdalabs_api.py`, `argparse`, `json`, `os`, and `sys`. It is usable from shell/Kconfig command substitutions to avoid selecting unavailable Lambda Labs capacity.

## Risks And Edge Cases
No API key or empty API results exit nonzero. Human output includes Unicode bullets/location markers, which may be unsuitable for strict ASCII parsers. The example help mentions `gpu_1x_h100_sxm5`; names must match API data exactly.

## Test Signals
Mock capacity maps for no key, API failure, empty capacity, specific instance with/without regions, `--pick-first`, JSON all-capacity output, and exit codes.
