# sources/test-tools/syzkaller/pkg/subsystem/extractor_test.go

## Purpose

This file unit-tests `Extractor` without depending on real path regexes or syzkaller program parsing. It validates the policy in `TracedExtract`: direct path matching, child-over-parent preference, handling conflicting reproducers, and using reproducers to disambiguate broad guilty path matches.

## Important APIs, Types, and Functions

The test constructs `Subsystem` objects for `fs`, `ext`, `nfs`, and `mm`, with a parent hierarchy rooted at an `all` subsystem. It uses `Extractor{raw: &testRawExtractor{...}}`, where `testRawExtractor` implements `FromPath` and `FromProg`. `progSubsystems` maps byte slices to mocked subsystem results via `reflect.DeepEqual`.

## Control Flow

The table-driven `TestExtractor` runs five crash scenarios. It checks that a single path returns the path subsystem, a reproducer child shadows a parent, conflicting reproducer children fall back to the path parent, a common repro subsystem wins over an irrelevant extra repro subsystem, and a repro child can select `fs/ext` when stack paths vote for both `mm` and `fs`.

## State, Dependencies, Risks, and Test Signals

All state is in-memory test fixture data. Dependencies are `testing`, `reflect`, and `testify/assert`. The tests intentionally use `ElementsMatch` because extraction order can depend on map iteration. The test signal is strong for the extractor's threshold and parent-pruning behavior, but it does not exercise `debugtracer` output, the `cutOff >= 3` unrelated-repro branch, empty crash lists, duplicate subsystem votes from one crash, or the production `rawExtractor` parser path.
