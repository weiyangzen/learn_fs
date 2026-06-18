# sources/test-tools/syzkaller/prog/clone.go

Purpose: deep-clones programs, calls, and arguments while preserving resource reference topology and use maps.

Important APIs/types/functions: `Prog.Clone`, `cloneWithMap`, `cloneCalls`, `cloneCall`, `CloneArg`, and internal `clone`.

Control flow and state: `Prog.Clone` creates a fresh `newargs` map so cloned `ResultArg` producers can be substituted into cloned consumer `Res` pointers. `clone` copies scalar arg structs, clones data byte slices, recurses through pointer/group/union contents, rebuilds `uses` for referenced resources, clears producer `uses` to be rebuilt, and records old-to-new result mappings.

Dependencies and integration: used heavily by mutation, minimization, collide transformations, and hints. Relies on `slices.Clone`, arg concrete types, `debugValidate`, and resource `uses` invariants.

Risks: unsafe programs intentionally panic on clone to avoid mutating VM-check/corpus-unsafe programs. Passing `nil` as `newargs` to clone detached calls/args keeps `Res` pointing at original producers, which is intentional for some collide duplication but dangerous if used incorrectly.

Test signals: clone behavior is indirectly covered by mutation, minimization, hints, collide, and serialization round-trip tests that mutate cloned programs and expect stable originals/resource references.
