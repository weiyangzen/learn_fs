# File Research: sources/virtualization/nbd/tests/Makefile.am

## Purpose
Top-level Automake test directory dispatcher.

## Main Contents
Defines `SUBDIRS = parse code run`, causing parse tests, C unit-style tests, and runtime integration tests to participate in the test build.

## Risks and Notes
All actual test definitions live in the child directories.
