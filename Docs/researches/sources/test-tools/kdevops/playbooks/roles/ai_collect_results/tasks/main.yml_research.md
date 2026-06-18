# sources/test-tools/kdevops/playbooks/roles/ai_collect_results/tasks/main.yml

Purpose: Ansible role tasks for collecting AI benchmark result JSON from remote hosts and generating local analysis artifacts.

Key APIs and flow: The role optionally includes `extra_vars.yaml`, sets local result/script directories on localhost, creates directories, copies analysis scripts, templates `analysis_config.json`, checks/fetches remote `results_*.json`, clears and recreates the local result directory, verifies collection, runs `analyze_results.py`, displays output, ensures graph directory, runs `generate_html_report.py`, and prints final paths.

State, dependencies, integration: Mutates local `workflows/ai/results` and `workflows/ai/scripts`, remote analysis directory, and fetched result files. Integrates Ansible `fetch`, local Python analyzers, and variables such as `ai_benchmark_results_dir` and `ai_benchmark_enable_graphing`.

Risks and test signals: It deletes the entire local results directory before collection; copied `generate_graphs.py` may be stale; extra-vars include always succeeds; ownership uses env `USER` for both owner and group. Tests should run syntax checks and fixture plays with no results, multiple hosts, graphing disabled, and analyzer failure.
