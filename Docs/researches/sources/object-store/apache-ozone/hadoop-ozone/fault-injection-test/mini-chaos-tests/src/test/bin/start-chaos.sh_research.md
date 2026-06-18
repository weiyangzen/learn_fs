<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/bin/start-chaos.sh -->
# sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/bin/start-chaos.sh

Final split target: `Docs/researches/sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/bin/start-chaos.sh_research.md`.

## Purpose
shell entrypoint that assembles classpath and starts the MiniOzone chaos test CLI. The file has 57 lines and was read in full for this research pass.

## Important APIs, Types, And Functions
Shell functions: `none`. Key commands/tools referenced: `mvn`. Sourced helpers: `none`.

## Control Flow
The script resolves its directory, moves to the repository root where needed, configures output/report variables, runs the check or install command, writes summary artifacts, and usually delegates common result handling to `_post_process.sh`.

## State And Persistence Behavior
State is written under `target/<check>` or configured `OUTPUT_DIR`, including `output.log`, `summary.txt`, counters, generated reports, tool caches in `.dev-tools`, and sometimes distribution/test artifacts.

## Dependencies And Integration Points
tools `mvn`.

## Risks And Edge Cases
- Shell scripts depend on repository-relative paths, external tools, and environment variables; missing tools or different working directories can change behavior.
- Parsing logs with grep/sed/awk is sensitive to Maven/tool output format changes.

## Test Signals
Signals come from chaos-test completion, propagated future exceptions, JUnit assertions in `LoadBucket`, mini-cluster readiness waits, and generated test reports.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/mini-chaos-tests/src/test/bin/start-chaos.sh -->
