# sources/test-tools/syzkaller/pkg/mgrconfig/testdata/gce1.cfg

Purpose: Canned Windows/GCE manager config fixture used by `TestCanned`.

Important content: Includes comments, `name` `windows-gce`, target `windows/amd64`, HTTP address, absolute workdir, syzkaller testdata path, non-root SSH user, procs 8, type `gce`, dashboard client/address, and VM config with count, machine type, and `gce_image`.

Control flow and state: Loaded through full config completion, then the `vm` object is parsed into `gce.Config`.

Dependencies and integration: Tests comment-tolerant config parsing, Windows target support, GCE VM schema, dashboard required fields, and syzkaller binary resolution in testdata.

Risks: Fixture paths must match repository testdata layout. It does not include image upload settings or SSH key permissions.

Test signals: Positive fixture for GCE image-name based config.
