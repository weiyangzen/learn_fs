# sources/test-tools/kdevops/playbooks/python/workflows/fstests/gen_results_summary

Purpose: Command-line wrapper around `gen_results_summary.py` for generating text summaries and optional merged xUnit XML from fstests result directories.

Key APIs and flow: `main()` parses `results_dir`, `--merge_file`, `--output_file`, `--verbose`, `--print_section`, and `--results_file`, then calls `gen_results_summary()`. If no matching result files are found, it exits with a message.

State, dependencies, integration: Does not implement parsing itself; all state changes are delegated to the module, which may write output and merged XML files. It imports from local `gen_results_summary`, so execution depends on the script directory being importable.

Risks and test signals: The wrapper uses `sys.exit(string)` for no-results, which reports failure with stderr text. It has no shebang environment portability beyond `/usr/bin/python3`. Tests should verify argument mapping, custom results file names, no-results exit behavior, and successful pass-through with output and merge files.
