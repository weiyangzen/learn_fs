# sources/test-tools/kdevops/playbooks/roles/ai_collect_results/files/generate_html_report.py

Purpose: Generates a static Milvus benchmark HTML report that combines summary metadata, graph references, filesystem sections, and detailed result rows.

Key APIs and flow: `HTML_TEMPLATE` defines the full page. `load_summary()` reads `graphs/summary.json` if present. `load_results()` filters JSON files with insert/query data, infers filesystem/block size from filenames and JSON, computes average query QPS, and sorts rows. Helpers generate table rows, configuration summary, and graph image snippets. `generate_html_report()` decides whether multi-filesystem sections are shown and fills the template.

State, dependencies, integration: Reads result JSON and graph summary files, writes one HTML file, and references graph paths under `graphs/`. Called by the AI collection role after `analyze_results.py`.

Risks and test signals: Header/table column counts are inconsistent: the template has six headers while rows emit seven cells. HTML values are not escaped; missing `summary.json` leaves zero best metrics even when results exist. Tests should validate generated HTML structure for single- and multi-filesystem fixtures.
