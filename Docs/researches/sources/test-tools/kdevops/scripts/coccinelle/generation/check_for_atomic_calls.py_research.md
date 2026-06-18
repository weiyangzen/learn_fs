# sources/test-tools/kdevops/scripts/coccinelle/generation/check_for_atomic_calls.py

Purpose: generates a Coccinelle semantic patch that traces transitive callers of a target function and reports callers reachable from likely atomic contexts.

Important APIs/types/functions: `argparse` requires `--levels`, `--target`, and `--output`; `multiprocessing.cpu_count`; generated SmPL rules include seed caller discovery, IRQ handler/name detection, per-level caller expansion, atomic primitive checks, lock-name checks, spinlock region checks, non-sleeping context checks, network driver context checks, atomic-name checks, and might-sleep checks.

Control flow: parses CLI, writes a Coccinelle file header with Python state sets and `register_caller`, then emits repeated rule blocks for each requested depth. The generated patch dynamically registers virtual identifiers to continue caller-chain exploration and prints warnings during `make coccicheck`.

State/persistence behavior: writes the requested `.cocci` output file. Runtime state inside the generated patch is in Coccinelle Python sets; no source code is modified by the generator.

Dependencies/integration: depends on Python 3 and Coccinelle/Kernel `make coccicheck MODE=report COCCI=<file>`. Integrates with kernel code analysis workflows.

Risks/test signals: comments mark confidence low; generated patterns are heuristic and can produce false positives/negatives. Some output uses Unicode symbols. Test signals are successful generator run, valid Coccinelle syntax, and actionable warning locations under coccicheck.
