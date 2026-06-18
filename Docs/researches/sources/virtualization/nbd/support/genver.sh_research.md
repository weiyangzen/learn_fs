# File Research: sources/virtualization/nbd/support/genver.sh

## Purpose
Generates a version string from Git metadata for build-time use.

## Behavior
Runs `git describe --dirty`, strips a leading `nbd-`, and falls back to `0.unknown` if no description is available. Prints the resulting string.

## Dependencies
Requires `/bin/sh`, `git`, and `sed` for the preferred path.

## Risks and Notes
The stderr redirection is attached to the `sed` command in the pipeline, so Git errors may still be visible depending on shell behavior. In non-Git source distributions, the fallback version is used.
