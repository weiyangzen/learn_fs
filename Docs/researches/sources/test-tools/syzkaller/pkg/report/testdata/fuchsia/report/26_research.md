# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/26

## Purpose
This fixture is a Fuchsia `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/26`. It feeds raw Zircon, Starnix, or Fuchsia component output into `Reporter.Parse` via `TestParse` and expects the normalized title `ASSERT FAILED in VmPageListNode::~VmPageListNode`.
It has no explicit `REPORT:` block, so the harness derives the expected report text from parser output while still checking title/type/corruption metadata.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `fuchsia.Parse`, `fuchsia.shortenReport`, `fuchsia.shortenStarnixPanicReport`, `fuchsia.symbolize`.
- Fixture metadata: TITLE=ASSERT FAILED in VmPageListNode::~VmPageListNode.
- Notable functions observed in the report body: `platform_halt`, `_panic`, `VmPageListNode::~VmPageListNode`, `fbl::unique_ptr::recycle`, `fbl::unique_ptr::reset`, `fbl::WAVLTree::clear`, `VmPageList::FreeAllPages`, `VmObjectPaged::~VmObjectPaged`.
- Notable source locations observed in the report body: `platform/pc/power.cpp:122`, `lib/debug/debug.cpp:40`, `vm/vm_page_list.cpp:31`, `system/ulib/fbl/include/fbl/unique_ptr.h:125`, `system/ulib/fbl/include/fbl/unique_ptr.h:65`, `system/ulib/fbl/include/fbl/intrusive_wavl_tree.h:391`, `vm/vm_page_list.cpp:170`, `system/ulib/fbl/include/fbl/ref_counted_internal.h:119`.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- Fuchsia-specific flow symbolically rewrites Zircon program counters when kernel objects are available, removes unrelated halt/build lines, and separately shortens Starnix panic stacks around frame-like lines.

## State And Persistence
- Static fixture only: 31 lines and 2128 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on the Fuchsia reporter configuration in `fuchsia.go`, the shared report parser in `report.go`, and test harness parsing in `report_test.go`. Symbolization may depend on configured kernel object paths but the fixture remains useful without modifying external state.

## Risks And Edge Cases
- Fuchsia logs contain timestamp prefixes, split assert lines, unrelated halt/build noise, and sometimes no explicit `REPORT:` block; small parser changes can alter boundaries or title normalization.

## Test Signals
- Primary signal: expected title `ASSERT FAILED in VmPageListNode::~VmPageListNode`.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `TITLE: ASSERT FAILED in VmPageListNode::~VmPageListNode`.
