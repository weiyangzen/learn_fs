# sources/test-tools/kdevops/scripts/coccinelle/generation/check_for_sleepy_calls.py

Purpose: generates a Coccinelle semantic patch that explores calls from a target function and reports paths to functions or flags that may sleep.

Important APIs/types/functions: `argparse` options `--function`, `--max-depth`, `--output`, optional `--sleepy-function`, `--expected`; lists of known sleepy functions and GFP flags; temporary stats directory; generated Coccinelle Python helpers `register_call`, `find_path_to`, `register_sleep_point`, `register_func_for_analysis`, `save_stats`, and final stats merge/cleanup.

Control flow: parses CLI, optionally narrows sleepy function list, creates a temp stats directory, writes SmPL rules to find direct calls from the target, optional direct sleepy calls, depth-expanded call discovery, known-sleeper/GFP/mutex/might_sleep/name-pattern checks, and a finalize block that merges per-process JSON stats and prints unique sleep paths.

State/persistence behavior: writes the requested `.cocci` output file and, when the generated patch runs, creates temporary JSON stats files under `/tmp/cocci_stats_<pid>` that are cleaned during finalize.

Dependencies/integration: depends on Python 3, Coccinelle, and kernel `make coccicheck`. Intended for conservative manual review of sleeping behavior.

Risks/test signals: script labels confidence low; generated finalize references variables in no-sleep path that may not be defined, and Coccinelle parallel stats aggregation uses max counters rather than full sums. Test signals are generator success, coccicheck syntax success, stats summary, and manually verified sleep paths.
