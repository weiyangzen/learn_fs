# sources/test-tools/syzkaller/pkg/cover/canonicalizer.go

Purpose: converts coverage PCs/signals between per-instance kernel module load addresses and a canonical module address layout so signals from different fuzzing VMs can be compared.

Important APIs/types/functions: `Canonicalizer`, `CanonicalizerInstance`, `Convert`, `canonicalizerModule`, `NewCanonicalizer`, `NewInstance`, `Canonicalize`, `Decanonicalize`, `findModule`, and `convertPCs`.

Control flow: `NewCanonicalizer` records canonical modules by name and sorted address keys only when module canonicalization is enabled by `flagSignal`. `NewInstance` builds forward and reverse conversion maps between instance and canonical modules, marking modules for discard if missing or size-mismatched. Conversion binary-searches the sorted module base keys; PCs inside known non-kernel modules receive offsets, discarded modules are dropped, and kernel or unknown unmapped PCs are passed through unless not found in a conversion hash.

State and persistence: in-memory module maps and conversion maps only. It logs discarded PC summaries but does not persist state.

Dependencies and integration: uses `vminfo.KernelModule` and `log`. It is designed for manager/RPC paths that ingest fuzzer coverage and fallback signals.

Risks: conversion assumes non-overlapping sorted module address ranges. Missing canonical modules discard coverage, which is correct for changed builds but can hide module coverage if discovery is incomplete. Offset arithmetic casts through `int64`, so very high address differences deserve care.

Test signals: `canonicalizer_test.go` covers nil modules, disabled signals, reordered modules, changing modules, coverage arrays, and bitmap conversion.
