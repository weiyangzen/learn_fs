# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-setup-pts

Purpose: provisions storage and state for Phoronix Test Suite runs on GCE.

Important flow: source configs, start `apt-get update` in background, prefer local SSD if present, otherwise create and attach a persistent SSD disk named `${instance}-disk` as `pts`. Format with `mkfs.$FSTESTTYP` if filesystem type differs, mount at `/pts`, restore PTS state/results tarballs from GCS if first use, bind mount `/pts/phoronix-test-suite` to `/var/lib/phoronix-test-suite`, wait for apt update, and install `pts/disk`.

State and dependencies: PTS disk/local SSD, `/pts`, `/var/lib/phoronix-test-suite`, GCS `pts-state.tar.xz`, `pts-results.tar.xz`, and per-instance results tarballs. Depends on gcloud, mkfs tools, GCS helpers, mount, and `phoronix-test-suite`.

Integration points: invoked by `gce-setup` when command mode is `pts`; `pts-save` later archives state/results.

Risks and test signals: formatting decision depends solely on `blkid TYPE`, so wrong target device is destructive. Local SSD state is ephemeral. Tests should validate idempotent remount and state restoration without reformatting.
