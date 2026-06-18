# sources/security-integrity/fscrypt/bin/files-changed

## Purpose
CI helper that fails if repository files changed after a generation or formatting step.

## APIs and Control Flow
The script checks `git status -s`. If dirty, it prints `git diff --minimal HEAD`, emits a banner tailored to `proto`, `format`, or generic mode, runs `git reset HEAD --hard`, and exits with status 1.

## State, Dependencies, and Integration
Depends on Git and assumes it runs in a repository where generated or formatted output should match committed files. It is likely called from Makefile or CI targets after `make gen` or `make format`.

## Risks and Test Signals
The script is destructive: it hard-resets all working tree changes. This is acceptable in CI but dangerous in an interactive developer tree. It has no local tests.
