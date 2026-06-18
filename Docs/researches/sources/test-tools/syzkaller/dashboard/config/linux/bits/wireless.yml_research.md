# sources/test-tools/syzkaller/dashboard/config/linux/bits/wireless.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for wireless fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 54 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: enables cfg80211/mac80211, hwsim, virtual wifi, selected ath/carl9170 drivers, WWAN/MHI, and disables most vendor families.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v5., v6., arm64, arm.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- arm64_gce hardware driver exclusions and removed WiMAX/RNDIS options.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.
