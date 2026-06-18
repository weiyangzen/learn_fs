# sources/test-tools/syzkaller/pkg/mgrconfig/testdata/gce2.cfg

Purpose: Canned Linux/GCE manager config fixture for `TestCanned`.

Important content: Defines `linux-gce`, target `linux/amd64`, HTTP/workdir/syzkaller/image paths, SSH user, procs 8, type `gce`, and VM config with count, machine type, and `gcs_path` for image upload.

Control flow and state: Full config loading verifies image path existence and GCE VM config parsing.

Dependencies and integration: Exercises GCE mode that uploads a local disk image to GCS rather than referencing an existing GCE image name.

Risks: Depends on `testdata/disk.raw` existence. Does not include dashboard/hub settings.

Test signals: Positive fixture for Linux GCE local-image upload config.
