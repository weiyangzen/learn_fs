# Research: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/cluster_args.py

- **Purpose:** Shared argparse construction for temporary cluster wrappers. It centralizes build-dir, process count, TLS, authorization, blob granule, and cleanup options.
- **Source facts:** 71 lines, 2473 bytes, executable=False.
- **Important APIs/types/functions:** Imports: argparse.ArgumentParser, argparse.RawDescriptionHelpFormatter. Classes: none. Top-level functions: CreateTmpFdbClusterArgParser. Methods: none. Constants: none. CLI flags/options observed: --authorization-keypair-id, --authorization-kty, --blob-granules-enabled, --build-dir, --client-cert-chain-len, --no-remove-at-exit, --process-number, --server-cert-chain-len, --tls-enabled, --tls-verify-peer, -b, -p.
- **Control flow:** Library-style helpers are called by neighboring test-runner modules; control flow is direct function or context-manager execution.
- **State and persistence:** keeps no durable state beyond function-local values
- **Dependencies:** Python imports: argparse.ArgumentParser, argparse.RawDescriptionHelpFormatter.
- **Integration points:** Used by neighboring FoundationDB test harness modules through package-relative imports or direct script execution.
- **Risks:** Risk is mainly integration drift with the surrounding test harness.
- **Test signals:** Observable signals include none; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
