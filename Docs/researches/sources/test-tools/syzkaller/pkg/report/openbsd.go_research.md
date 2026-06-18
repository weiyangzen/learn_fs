# Research: sources/test-tools/syzkaller/pkg/report/openbsd.go

Purpose: configures the shared BSD reporter for OpenBSD crash logs. It defines OpenBSD panic/witness/uvm fault/kernel trap title formats and suppresses known unhelpful panics.

Important APIs/types/functions: `ctorOpenbsd` sets stack and witness symbolization regexps, calls `ctorBSD`, and returns suppressions for `vop_generic_badop`, repetitive witness inode lock reversals, and broken-pipe disconnect panics. `openbsdOopses` handles cleaned vnode, many panic subformats, witness lock issues, `uvm_fault`, kernel page/protection traps, group Go runtime errors, and common syzkaller failures.

Control flow: the constructor builds a `bsd` reporter with OpenBSD-specific tables. Parsing is line-based through `simpleLineParser`; title selection prefers more specific panic/witness/uvm regexps before generic corrupted fallbacks. Symbolization is inherited from `bsd` using OpenBSD frame forms like `at func+0xoff` and witness `#N func+0xoff`.

State and persistence: no OpenBSD-specific mutable state beyond suppressions and regex tables. Optional symbol state is held by the embedded `bsd` reporter.

Dependencies and integration points: selected by `ctors[targets.OpenBSD]`. It integrates with common report normalization, shared BSD symbolization, and the generic test fixture runner.

Risks: OpenBSD debugger output includes prompts and carriage-return quirks, so start/end offsets are more fragile than line-only parsing suggests. Broad panic regexps can normalize away detail; suppressions must not mask actionable lock issues. `uvm_fault` has both complete and corrupted formats, so ordering matters.

Test signals: `openbsd_test.go` covers symbolization; parse fixtures under `testdata/openbsd/report` should cover panic, witness, uvm, and kernel trap cases.
