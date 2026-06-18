# sources/security-integrity/gocryptfs/cli_args.go

Purpose: This file defines gocryptfs command-line option parsing and stores parsed options in `argContainer`.

Important APIs and functions: `argContainer` contains operation flags, mount flags, crypto flags, profiling paths, FIDO2 options, exclusion rules, config overrides, and internal parsed state. `prefixOArgs` converts mount-style `-o a,b` options into normal flags. `convertToDoubleDash` preserves compatibility after moving to `pflag`. `parseCliOpts`, `prettyArgs`, `countOpFlags`, and `isFlagPassed` implement parsing and validation.

Control flow and state: Parsing preprocesses args, registers all flags, handles tri-state OpenSSL auto mode, rejects incompatible password/master-key/FIDO options, validates badname globs and long-name thresholds, and records explicitly passed scrypt cost.

Dependencies and integration points: Feeds main init/mount/passwd/info/fsck control flow, configfile creation, crypto backend selection, FUSE mount options, and reverse-mode exclusions.

Risks and test signals: CLI compatibility is high-risk. Known dash-duplication behavior around `-extpass -X` is documented. Signals include parsing tests for `-o`, single/double dash conversion, option conflicts, OpenSSL auto selection, and operation flag counts.
