# sources/storage-engines/pebble/scripts/stress-new-tests.sh

## Purpose
This script finds newly added Go test functions relative to a base branch and stress-runs only those tests package by package.

## Important APIs, Types, and Functions
It defaults `BASE_BRANCH` to `origin/master`, loops over `go list ./...`, normalizes module paths to relative package paths, extracts added `func Test...` names from zero-context git diff hunks, builds a `-run` regex, and runs `go test --tags invariants --exec 'stress ...'`.

## Control Flow
For each package with added tests, it prints the stress command and runs it with `stress -p 2 --maxruns 1000 --maxtime 10m --timeout 2m`. On first failure it prints the package/test regex and exits 1. If no failures occur, it prints a success message.

## State and Persistence Behavior
No persistent state is intentionally written beyond normal test artifacts.

## Dependencies and Integration Points
It depends on Go, git, grep, awk, cut, paste, sort, and the `stress` binary. It integrates with PR validation workflows focused on new tests.

## Risks
The parser only catches lines beginning `+func Test`, missing methods, fuzz tests, examples, or multiline declarations. It uses Unicode status symbols in output. Diffing package `*.go` paths can miss tests in unusual generated locations.

## Test Signals
A successful run means all detected new test functions survived stress settings. Failure exits at the first failing package.
