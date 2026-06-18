# File Research: sources/virtualization/spdk/app/nvmf_tgt/nvmf_main.c

## Purpose
Minimal executable wrapper for the SPDK NVMe-oF target app.

## Main Entry Points
- `nvmf_usage()` and `nvmf_parse_arg()` provide empty app-specific argument handling.
- `nvmf_tgt_started()` optionally dumps memzones when `MEMZONE_DUMP` is set.
- `main()` initializes SPDK app opts, parses args, starts the app framework, finalizes, and returns status.

## Internal Mechanics
The app name is `nvmf`. All meaningful target setup and runtime behavior come from linked event subsystems and configuration/RPC processing.

## Dependencies
Uses SPDK stdinc, env, and event APIs.

## Filesystem/Block Relevance
This is the process entry point for the NVMe-oF target that exports SPDK bdevs.

## Risks and Notes
- No custom app-specific CLI options are implemented.
- Startup blocks until the SPDK app exits.
