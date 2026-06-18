# Research: sources/test-tools/kdevops/playbooks/roles/mmtests_compare/files/generate_html_with_graphs.sh

`sources/test-tools/kdevops/playbooks/roles/mmtests_compare/files/generate_html_with_graphs.sh` is a support file in the kdevops `mmtests_compare` role. Role context: compares mmtests benchmark result sets and generates HTML/graph reports. The file is 90 lines / 2953 bytes and was read in full for this report.

## Purpose

This shell helper supports `mmtests_compare` by orchestrating command-line benchmark/report operations. It is intended to be called by Ansible or another local wrapper as part of the role workflow.

## Important APIs, Types, And Functions

External commands/control keywords used include `--baseline`, `--compare`, `--format`, `--output-dir`, `--report-title`, `../../compare-kernels.sh`, `>`, `BASELINE_NAME=$3`, `BENCHMARK=$2`, `DEV_NAME=$4`, `OUTPUT_DIR=$5`, `OUTPUT_DIR=$TOPDIR/$OUTPUT_DIR`, `PNG_COUNT=$(ls`, `TOPDIR=$1`, `cd`, `echo`, `else`, `exit`, plus 8 more. Shell variables referenced include `BASELINE_NAME`, `BENCHMARK`, `DEV_NAME`, `OUTPUT_DIR`, `PNG_COUNT`, `R_TMPDIR`, `TOPDIR`, `ls`.

## Control Flow

Control flow is POSIX/bash command sequencing with argument parsing, validations, loops/conditionals where present, and explicit exits on failure. The script delegates heavy work to external tools such as mmtests, gnuplot, Perl, or HTML-processing utilities depending on its filename and command list.

## State And Persistence

State is persisted through generated archives, comparison data, graph images, patched source trees, or HTML files in paths passed by the caller. Temporary files and command side effects must be cleaned by the caller or by traps/cleanup logic inside the script.

## Dependencies And Integration Points

It depends on shell tools `--baseline`, `--compare`, `--format`, `--output-dir`, `--report-title`, `../../compare-kernels.sh`, `>`, `BASELINE_NAME=$3`, `BENCHMARK=$2`, `DEV_NAME=$4`, `OUTPUT_DIR=$5`, `OUTPUT_DIR=$TOPDIR/$OUTPUT_DIR`, `PNG_COUNT=$(ls`, `TOPDIR=$1`, `cd`, `echo`, `else`, `exit`, `export`, `fi`, plus 6 more plus the mmtests comparison directory layout established by `mmtests_compare/tasks/main.yml`. Ansible copies or invokes these scripts and then fetches/generated artifacts for final reports.

## Risks And Edge Cases

Risks include missing executable dependencies, unquoted paths, partial graph/report generation, failed patches, and input result directories that do not match mmtests expectations. Exit-code handling is the primary contract for callers.

## Test Signals

Validate with `bash -n`, run against small fixture result directories, and confirm expected output files, nonzero failures for bad input, and Ansible task return codes.
