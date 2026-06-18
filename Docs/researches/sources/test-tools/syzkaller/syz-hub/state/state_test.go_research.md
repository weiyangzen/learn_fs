## sources/test-tools/syzkaller/syz-hub/state/state_test.go

This file tests syz-hub state persistence and exchange semantics. `TestBasic` ensures unconnected managers cannot sync and a connected manager can sync. `TestRepro` validates repro delivery only to compatible managers that did not originate the repro, duplicate handling, call-set filtering, and persistence after reload. `TestDomain` validates domain-tag propagation for shared corpus inputs across managers and after reload.

Helpers create temp-backed states, connect managers, sync sorted outputs, add repros, and reload state. Coverage is strong for core state behavior but does not test stale-manager purge, large pending-input caps, invalid corpus cleanup, or concurrent hub access.
