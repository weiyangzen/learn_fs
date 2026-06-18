# sources/test-tools/kdevops/scripts/lambda-cli

## Purpose
`lambda-cli` is a Python command-line interface for Lambda Labs cloud data used by kdevops. It lists instance types and regions, reports pricing, chooses simple automatic instance/region selections, checks availability, and generates Kconfig fragments.

## Important APIs, Types, And Functions
The main type is `LambdaCLI`, with methods `output()`, `list_instance_types()`, `list_regions()`, `get_cheapest_instance()`, `get_pricing()`, `smart_select()`, `check_availability()`, and `generate_kconfig()`. `main()` builds an argparse command tree for `instance-types`, `regions`, `pricing`, `smart-select`, `check-availability`, and `generate-kconfig`.

## Control Flow
`LambdaCLI.__init__()` loads an API key through `lambdalabs_api.get_api_key()`. Each command queries API helpers and formats JSON or text. `get_cheapest_instance()` filters available capacity and minimum GPU count, then chooses the lowest hardcoded price. `smart_select()` currently implements `cheapest` and a simplified `balanced` mode, while `closest` returns a placeholder error. `generate_kconfig()` writes generated compute/location/mapping files.

## State And Persistence
Runtime state is the output format and API key. Persistent writes occur only in `generate_kconfig()`, which creates an output directory and writes generated Kconfig files. No credentials are written by this script.

## Dependencies And Integration Points
Depends on `lambdalabs_api.py`, `argparse`, `json`, `os`, `sys`, and standard typing/path libraries. Wrapper scripts `lambdalabs_smart_inference.py` and `lambdalabs_infer_region.py` call it as a subprocess. Kconfig generation integrates with `terraform/lambdalabs/kconfigs`.

## Risks And Edge Cases
The local source contains apparent syntax errors: duplicated `def get_pricing(...)` and an extra `)` after `kconfig_parser.add_argument(...)`. If present, the CLI cannot run, which also breaks wrapper scripts. Pricing is hardcoded and may drift from Lambda Labs. Minimum GPU parsing assumes names like `gpu_8x_*`. Text output tables can become wide.

## Test Signals
Run `python3 -m py_compile scripts/lambda-cli`, then mock API helpers for each subcommand, no-API-key paths, JSON/text output, cheapest selection with filters, Kconfig generation file writes, and wrapper-script subprocess behavior.
