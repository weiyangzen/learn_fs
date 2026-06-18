# sources/test-tools/syzkaller/pkg/subsystem/linux/maintainers_test.go

## Purpose

This test file verifies two critical MAINTAINERS behaviors: conversion of raw `maintainersRecord` path metadata into matchable `PathRule`s, and parsing representative MAINTAINERS text into structured records.

## Important APIs, Types, and Functions

`TestRecordToPathRule` builds records and matches paths through `subsystem.MakePathMatcher`. `TestLinuxMaintainers` calls `parseLinuxMaintainers` with `maintainersSample` and compares the resulting `maintainersRecord` slice. The sample covers maintainers, lists, trees, include/exclude rules, regexps, comments, ignored property keys, and list annotations such as `(subscribers-only)`.

## Control Flow

Path-rule tests cover wildcard expansion, `?` matching, directory recursion, `N` regex inclusion, exclusion precedence, trailing slash handling, escaping literal dots, and match-everything patterns. The parser test skips the prose header, ignores note/comment blocks, collects known properties, tolerates extra mailing-list suffix text through `parseEmail`, and verifies the exact normalized records.

## State, Dependencies, Risks, and Test Signals

State is local test fixture data. Dependencies are `strings`, `testing`, the local `linux` package, `subsystem.PathMatcher`, and `testify/require`. These tests provide strong regression signals for matching semantics used by subsystem generation. They do not cover parse errors, invalid regexps, scanner length limits, platform-specific path separators beyond the implementation default, or all MAINTAINERS property keys.
