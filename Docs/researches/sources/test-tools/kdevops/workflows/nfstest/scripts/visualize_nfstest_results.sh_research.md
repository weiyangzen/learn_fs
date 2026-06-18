# sources/test-tools/kdevops/workflows/nfstest/scripts/visualize_nfstest_results.sh

## Purpose
Shell wrapper that turns existing nfstest run logs into an HTML visualization. It validates the result directory, calls the Python parser, calls the HTML generator, and reports the generated output location.

## Important APIs, Types, and Functions
This is a Bash CLI script rather than a library. Important variables are `SCRIPT_DIR`, resolved from `readlink -f "$0"`; `KDEVOPS_DIR`, resolved from `git rev-parse --show-toplevel` with `pwd` fallback; `RESULTS_DIR`, defaulting to `$KDEVOPS_DIR/workflows/nfstest/results/last-run` unless argv[1] is supplied; and `HTML_OUTPUT_DIR`, fixed at `$KDEVOPS_DIR/workflows/nfstest/results/html`.

## Control Flow
The script exits early if `RESULTS_DIR` does not exist or contains no `*.log` files. It then runs `python3 "$SCRIPT_DIR/parse_nfstest_results.py" "$RESULTS_DIR"` and treats a nonzero exit as fatal. Next it runs `python3 "$SCRIPT_DIR/generate_nfstest_html.py" "$RESULTS_DIR"` and prints a warning, not a fatal error, on nonzero status. Final success requires `$HTML_OUTPUT_DIR/index.html`; if present, the script prints open/scp hints and lists generated files, otherwise it exits with an error.

## State and Persistence Behavior
The wrapper itself keeps no durable state. Its child parser writes `parsed_results.json` under the result directory, and the HTML generator is expected to write under `workflows/nfstest/results/html`. Existing parsed JSON or HTML files may be overwritten by those child scripts. Output paths are global to the workflow rather than per-kernel or per-run, so repeated visualizations can replace prior HTML.

## Dependencies and Integration Points
Requires Bash, `readlink -f`, Git if repository-root discovery should work, `find`, `wc`, `python3`, `ls`, `parse_nfstest_results.py`, and `generate_nfstest_html.py`. The user-facing error text points to `make nfstest-baseline` and `make nfstest-dev`, so it is integrated with the kdevops nfstest Make targets and expected results layout.

## Risks
There is no `set -euo pipefail`, so only explicitly checked commands affect control flow. `LOG_COUNT=$(find ... | wc -l)` includes whitespace from `wc`, which is accepted by numeric `[` in typical shells but is still a brittle pattern. HTML generation can fail but still be considered acceptable until the final `index.html` check, which may pass with stale HTML if a previous run left the file in place. `SCRIPT_DIR` relies on GNU-compatible `readlink -f`. The fixed `HTML_OUTPUT_DIR` ignores a custom result directory, which may surprise users visualizing non-default runs.

## Test Signals
Shell tests should cover missing results directory, empty results directory, parser failure, HTML generator failure with no stale index, custom `RESULTS_DIR`, and operation outside a Git checkout. A practical smoke test is to create a temporary result tree with one `.log`, run the wrapper, and verify `parsed_results.json` plus `workflows/nfstest/results/html/index.html`.
