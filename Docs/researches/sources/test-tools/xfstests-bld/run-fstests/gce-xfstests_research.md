# sources/test-tools/xfstests-bld/run-fstests/gce-xfstests

Purpose: primary Google Compute Engine runner and administration CLI for xfstests. It manages GCS artifacts/config, instance/disk/image/result commands, kernel uploads, LTM/KCS delegation, machine-type selection, and test VM creation.

Important functions: `get_local_hash`, `get_remote_hash`, `verify_single_uri`, `do_get_results_uri`, `do_get_results`, `get_gce_zone`, `get_gce_zone_disk`, `get_machtype_file`, `get_machtype_stats`, `fit_machtype_resources`, and `launch_vm`. It also exposes many subcommands through a large `case`: list/remove/start/stop instances, disks, images, results, ssh/scp/console/serial/describe, setup, image import/export/copy, kbuild/install-kconfig, upload-kernel, LTM/KCS launch/control, dashboard launch, and normal test launch.

Control flow: validates core config, handles early administrative subcommands, ensures bucket config exists, syncs selected config variables to `gs://$GS_BUCKET/gce_xfstests.config`, parses CLI for a test launch, computes test run id/instance name, resolves kernel/modules/hooks/test files to GCS URIs with hash-based upload avoidance, appends metadata arguments, chooses or validates a machine type, delegates to LTM/KCS if requested, ensures cert freshness, then creates a Compute Engine VM with metadata containing the xfstests command payload and retries selected resource/image-family failures.

State/persistence: persists GCS config/artifacts/results, local cache files under `$GCE_CACHE_DIR`, local config cache in `/tmp`, optional `.ltm_instance_$GCE_PROJECT`/`.kcs_instance_$GCE_PROJECT`, VM metadata, created instances/disks, and result tarballs under `/tmp` when fetched.

Dependencies/integration: depends heavily on shared util scripts (`get-config`, `parse_opt_funcs`, `arch-funcs`, `parse_cli`, LTM/KCS funcs), gcloud wrappers, GCS bucket/project/zone config, jq, openssl, sed/awk/tar/xz, kernel artifact introspection, and GCE image families.

Risks: very large shell script with many global variables and side-effectful subcommands. Metadata argument construction relies on shell quoting and `--metadata "^ ^$ARG"`. Hard-coded machine pricing can go stale. There is a syntax-looking bug in the cert check: `if test -f "$cert_file" ! openssl ...` is missing a command separator/operator. Remote deletion/upload commands are powerful and need careful project/bucket targeting.

Test signals: no-action launch output, `get-results` fixture tarballs, machine-type cache refresh, upload-kernel hash checks, and GCE integration tests for VM creation/deletion are needed. LTM/KCS paths require separate service tests.
