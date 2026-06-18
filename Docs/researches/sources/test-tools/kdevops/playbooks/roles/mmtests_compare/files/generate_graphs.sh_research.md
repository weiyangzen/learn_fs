# Research: sources/test-tools/kdevops/playbooks/roles/mmtests_compare/files/generate_graphs.sh

`sources/test-tools/kdevops/playbooks/roles/mmtests_compare/files/generate_graphs.sh` is a support file in the kdevops `mmtests_compare` role. Role context: compares mmtests benchmark result sets and generates HTML/graph reports. The file is 149 lines / 4933 bytes and was read in full for this report.

## Purpose

This shell helper supports `mmtests_compare` by orchestrating command-line benchmark/report operations. It is intended to be called by Ansible or another local wrapper as part of the role workflow.

## Important APIs, Types, And Functions

External commands/control keywords used include `--format`, `--output`, `--print-monitor`, `--sort-samples-reverse`, `--title`, `--with-smooth`, `--x-label`, `-b`, `-d`, `-n`, `./bin/graph-mmtests.sh`, `.container`, `.description`, `.graph`, `<!DOCTYPE`, `</head>`, `</style>`, `<body>`, plus 33 more. Shell variables referenced include `BASELINE_NAME`, `BENCHMARK`, `DEV_NAME`, `KERNEL_LIST`, `OUTPUT_DIR`, `TOPDIR`, `basename`, `graph`, `graphname`, `kernel`, `monitor_type`, `title`.

## Control Flow

Control flow is POSIX/bash command sequencing with argument parsing, validations, loops/conditionals where present, and explicit exits on failure. The script delegates heavy work to external tools such as mmtests, gnuplot, Perl, or HTML-processing utilities depending on its filename and command list.

## State And Persistence

State is persisted through generated archives, comparison data, graph images, patched source trees, or HTML files in paths passed by the caller. Temporary files and command side effects must be cleaned by the caller or by traps/cleanup logic inside the script.

## Dependencies And Integration Points

It depends on shell tools `--format`, `--output`, `--print-monitor`, `--sort-samples-reverse`, `--title`, `--with-smooth`, `--x-label`, `-b`, `-d`, `-n`, `./bin/graph-mmtests.sh`, `.container`, `.description`, `.graph`, `<!DOCTYPE`, `</head>`, `</style>`, `<body>`, `<div`, `<h1>mmtests`, plus 31 more plus the mmtests comparison directory layout established by `mmtests_compare/tasks/main.yml`. Ansible copies or invokes these scripts and then fetches/generated artifacts for final reports.

## Risks And Edge Cases

Risks include missing executable dependencies, unquoted paths, partial graph/report generation, failed patches, and input result directories that do not match mmtests expectations. Exit-code handling is the primary contract for callers.

## Test Signals

Validate with `bash -n`, run against small fixture result directories, and confirm expected output files, nonzero failures for bad input, and Ansible task return codes.
