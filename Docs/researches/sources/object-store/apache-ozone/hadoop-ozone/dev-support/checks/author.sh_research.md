<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/dev-support/checks/author.sh -->
# sources/object-store/apache-ozone/hadoop-ozone/dev-support/checks/author.sh

Final split target: `Docs/researches/sources/object-store/apache-ozone/hadoop-ozone/dev-support/checks/author.sh_research.md`.

## Purpose
source hygiene check that fails when Java files contain `@author` tags. The file has 34 lines and was read in full for this research pass.

## Important APIs, Types, And Functions
Shell functions: `none`. Key commands/tools referenced: `grep`. Sourced helpers: `${DIR}/_post_process.sh`.

## Control Flow
The script resolves its directory, moves to the repository root where needed, configures output/report variables, runs the check or install command, writes summary artifacts, and usually delegates common result handling to `_post_process.sh`.

## State And Persistence Behavior
State is written under `target/<check>` or configured `OUTPUT_DIR`, including `output.log`, `summary.txt`, counters, generated reports, tool caches in `.dev-tools`, and sometimes distribution/test artifacts.

## Dependencies And Integration Points
tools `grep`; sourced helpers `${DIR}/_post_process.sh`.

## Risks And Edge Cases
- Shell scripts depend on repository-relative paths, external tools, and environment variables; missing tools or different working directories can change behavior.
- Parsing logs with grep/sed/awk is sensitive to Maven/tool output format changes.

## Test Signals
This file is itself CI/check infrastructure; expected signal is the produced `summary.txt`, `failures`, logs, and post-processed exit code.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/dev-support/checks/author.sh -->
