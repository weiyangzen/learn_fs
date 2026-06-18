# sources/sync-backup/casync/test/test-cautil.c

Purpose: unit tests locator utility functions.

Important APIs/types/functions: tests `ca_locator_has_suffix`, `ca_strip_file_url`, `ca_classify_locator`, and `ca_locator_patch_last_component` across path, file URL, HTTP URL, and SSH-like locator examples.

Control flow/state: pure string tests allocate/free patched strings and compare exact expected outputs.

Dependencies/integration: covers `cautil` functions used by CLI and remoting locator handling.

Risks/test signals: good guard for parsing edge cases involving query strings, localhost file URLs, and SSH colon syntax. It does not cover every URL escaping case.

Source research group: `subset-b-009122`.
