<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba_kcc -->
# sources/user-network-fs/samba/source4/scripting/bin/samba_kcc

Purpose: command-line entry point for the Samba Knowledge Consistency Checker, computing and optionally applying AD replication topology.

Important APIs/types/functions: `KCC`, `test_all_reps_from`, `verify_and_dot`, `list_verify_tests`, `GraphError`, and options such as `--readonly`, `--verify`, `--dot-file-dir`, `--importldif`, `--exportldif`, `--forced-local-dsa`, `--test-all-reps-from`, and link-forgetting flags.

Control flow: options configure logging, deterministic randomness, time override, credentials, and DB URL. Export exits after dumping topology LDIF. Import creates a temporary DB from LDIF and refuses to clobber an existing temp DB. The main path loads samdb, optionally lists valid DSAs or runs `test_all_reps_from`, and then calls `kcc.run` with topology mutation or read-only calculation.

State and persistence behavior: normal runs can write NTDS connection/topology changes to samdb unless `--readonly` is set. Import mode creates a temporary schemaless DB. Dot output writes Graphviz files. The test-all path repeatedly reconstructs KCC state for each DSA.

Dependencies and integration points: integrates with `samba.kcc`, graph verification, credentials, live DSA connection tests, LDIF import/export helpers, and AD replication metadata in samdb.

Risks: non-readonly runs alter replication topology. `--attempt-live-connections` adds network dependency. Import temp DB protection avoids accidental overwrite, but DB URL/import combinations are rejected only by option checks. Time and random seed options can change topology decisions.

Test signals: graph verifier errors, generated dot graphs, exit codes from `kcc.run`, listed verify tests, and read-only output are direct signals. `--test-all-reps-from` is useful for broad topology consistency validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba_kcc -->
