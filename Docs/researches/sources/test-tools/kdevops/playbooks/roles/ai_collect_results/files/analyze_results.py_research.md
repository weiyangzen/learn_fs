# sources/test-tools/kdevops/playbooks/roles/ai_collect_results/files/analyze_results.py

Purpose: Main AI benchmark analysis tool that loads Milvus benchmark JSON, collects DUT metadata, writes text/HTML reports, generates graphs, and saves consolidated JSON.

Key APIs and flow: `ResultsAnalyzer` owns state. Initialization creates the output directory and collects system, storage, virtualization, and filesystem details via `/proc`, `lsblk`, `nvme`, `systemd-detect-virt`, `dmesg`, and `df`. `load_results()` reads `results_*.json`. Summary and HTML methods aggregate insert, index, and query performance by node and filesystem config. `generate_graphs()` calls five plot methods for insert, query, index, matrix, and node/filesystem comparison. `analyze()` orchestrates all artifacts.

State, dependencies, integration: Writes `benchmark_summary.txt`, `benchmark_report.html`, graph images, and `consolidated_results.json`. Optional graph imports degrade gracefully. Called by `ai_collect_results` Ansible tasks.

Risks and test signals: HTML is string-built without escaping; local DUT info may describe the collector, not remote nodes; filename parsing is policy-heavy; external commands may need privileges. Tests should use fixture JSON for baseline/dev, disabled graph libs, missing fields, and mocked subprocess results.
