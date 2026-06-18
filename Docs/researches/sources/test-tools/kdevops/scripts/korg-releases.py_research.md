# sources/test-tools/kdevops/scripts/korg-releases.py

## Purpose
`korg-releases.py` queries `https://www.kernel.org/releases.json` and prints release references for a requested moniker such as `mainline`, `stable`, `longterm`, or `linux-next`. It is suitable for Kconfig shell-generated choices or automation that needs current kernel release tags.

## Important APIs, Types, And Functions
Functions are `parser()`, `_check_connection()`, `kreleases(args)`, and `main()`. Command-line options include `--moniker` (required), `--pname`, `--pversion`, and `--debug`.

## Control Flow
`main()` configures logging, parses known args, and calls `kreleases()`. `kreleases()` first checks TCP connectivity to `kernel.org:80`, then fetches the HTTPS releases JSON with a project User-Agent. It filters releases by moniker, prefixes semantic versions with `v`, preserves non-matching version strings as-is, and prints each reference.

## State And Persistence
No persistent state is written. Runtime output depends on network reachability and the current kernel.org JSON.

## Dependencies And Integration Points
Depends on Python standard libraries `argparse`, `json`, `urllib.request`, `socket`, `logging`, and `re`. It integrates with any Kconfig or build logic that shells out to populate kernel version options.

## Risks And Edge Cases
Connectivity is checked on port 80 while data is fetched over HTTPS port 443, so the precheck can be misleading. Network errors raise and are caught only at the top level, printing a traceback and exiting 1. The regex only handles `x.y`, `x.y.z`, and `x.y-rcN`.

## Test Signals
Mock `urllib.request.urlopen` and `_check_connection()` for online/offline paths, moniker filtering, semantic tag prefixing, linux-next strings, debug logging, and exception exit behavior.
