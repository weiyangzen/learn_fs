<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/compute/git-annex-compute-singularity -->
# sources/sync-backup/git-annex/doc/special_remotes/compute/git-annex-compute-singularity

Purpose: git-annex compute remote program for running Singularity containers whose image and inputs are stored in the annex.

Important functions and options: `run_singularity` invokes `singularity run --net --network=none --oci --bind="$binddir" --pwd="$rundir"` with optional `--no-compat` and `--fakeroot`. `strip_escape` removes ESC bytes from container output before forwarding to stderr. The argument parser uses `--` separators for stages: container/options/inputs, outputs, and command parameters.

Control flow: without `ANNEX_COMPUTE_passthrough`, the script requests each stage-1 non-option as `INPUT`, hard-links the resolved input into the current sandbox path, treats the first input as the container, requests stage-2 paths as `OUTPUT`, then runs Singularity with remaining arguments and stdin closed. With passthrough enabled, it asks git-annex for `SANDBOX`, binds the sandbox top, requires the passthrough container path through `INPUT-REQUIRED`, and lets stdio pass through to a command inside the container.

State and persistence: creates directories and hard links in the working sandbox. It does not persist configuration, but it depends on git-annex-provided sandbox paths and environment variables.

Dependencies and integration points: Bash, Singularity, `realpath`, process substitution, git-annex compute protocol, and host support for OCI/process namespaces.

Risks: hard-linking requires compatible filesystems and can fail across devices. Network disabling is helpful but not a complete sandbox policy; bind mounts expose the sandbox tree. It only strips ESC characters, not all terminal control sequences. `--fakeroot` broadens behavior and depends on host configuration.

Test signals: exercise normal and passthrough modes, multiple input/output stages, missing container failures, network isolation, stderr sanitization, and hard-link behavior across filesystems.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/doc/special_remotes/compute/git-annex-compute-singularity -->
