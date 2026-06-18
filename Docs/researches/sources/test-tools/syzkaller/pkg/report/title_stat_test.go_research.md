# sources/test-tools/syzkaller/pkg/report/title_stat_test.go

## Purpose

This test validates the JSON-backed crash-title trie update logic from `title_stat.go`.

## Important APIs, Types, And Flow

`TestAddTitleStat` uses table-driven cases with temporary files. Each case calls `AddTitleStat` zero or more times, then `ReadStatFile`, and compares the resulting nested `titleStat` structure with `testify/assert`. The scenarios cover an empty read, one report title, a two-title chain, and two chains sharing the same first title but diverging at the second.

## State, Dependencies, Risks, And Test Signals

The tests persist state only inside `t.TempDir`. They exercise the real JSON read/write path and the recursive count/node allocation behavior. They do not cover `visit`, malformed existing files, or concurrent modification, so those remain residual risks. The strongest signal is that counts increment at each prefix node, not just at leaves.
