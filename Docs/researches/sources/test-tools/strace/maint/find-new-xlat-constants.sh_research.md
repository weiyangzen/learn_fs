# sources/test-tools/strace/maint/find-new-xlat-constants.sh

Purpose: compares Linux kernel header constants across a commit range and reports constants newly added upstream that are not represented in existing strace xlat tables.

Important APIs/types/functions: shell functions `extract_xlat_constants`, `extract_prefix_directive`, `extract_pattern_directive`, `calculate_prefix`, `extract_all_header_constants`, prefix/pattern filters, and `process_line`. It uses Git object access, `sed`, `awk`, `grep`, `comm`, `sort`, and temporary files.

Control flow: validates `-d LINUX_REPO` and a two-dot commit range, verifies both commits, creates temp files, reads a tab-separated table from stdin (`xlat_file`, `line_type`, `header_file`), skips missing files/headers, extracts constants already in xlat, derives a matching prefix or uses `#Prefix`/`#Pattern`, extracts matching constants from both commits, then prints rows where constants exist in the newer commit but not the older commit or xlat.

State and persistence behavior: changes directory briefly for Git validation, then processes through temp files removed by traps. It emits report rows to stdout and does not modify xlat files.

Dependencies and integration points: pairs with `list-xlat-linux-headers.sh -t -c` to build the input table. It integrates kernel-header update review with strace xlat maintenance.

Risks: prefix inference can be too broad or too narrow; regex extraction of enum and define names can include false positives or miss lower/macro-expression constants. Only two-dot ranges are accepted. `comm` correctness depends on sorted inputs.

Test signals: running against known Linux tag ranges should identify expected new constants without noisy unrelated rows; shellcheck-like validation and temp cleanup on interrupts are useful operational checks.
