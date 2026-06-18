# sources/test-tools/syzkaller/executor/embed.go

Purpose: Builds a single embedded common-header blob for `pkg/csource` so generated C reproducers can include executor support code without a source-tree include graph.

Important APIs and control flow: `src` embeds `common*.h`, `kvm*.h`, and `android/*.h`. `CommonHeader` reads `common.h`, discovers all other embedded headers except `common.h` and `common_ext_example.h`, then repeatedly replaces `#include "name.h"` and `#include "android/name.h"` with embedded contents until no more replacements occur. It panics if any embedded header was unused. Finally it removes ordinary `//` comments while preserving `//%` license/comment lines used by imported code.

State and dependencies: package-level initialization computes `CommonHeader` once. It uses `embed.FS`, `fs.Glob`, `maps.Clone`, `bytes.ReplaceAll`, `path.Base`, and regex cleanup.

Integration points: csource generation consumes `executor.CommonHeader`; `style_test.go` enforces source patterns that make this textual include/comment stripping safe.

Risks and tests: include replacement is basename-based, so duplicate basenames across directories would be ambiguous except for the special android path check. The variable name `relacedSomething` is misspelled but harmless. Comment stripping is regex-based and can break unusual string/comment patterns; style rules reduce that risk.
