# File Research: sources/os/plan9/9front/sys/src/cmd/venti/words/dumpvacroots

`dumpvacroots` is an rc script that scrapes the Venti HTTP `/index` page, derives arena print commands, runs `venti/printarena`, and extracts clumps of type 16 as `vac:<score>` roots.

The script demonstrates that anyone with physical arena access or HTTP index visibility can enumerate historical vac roots. It depends on `hget`, `sed`, `awk`, `rc`, and the `$venti` environment variable.
