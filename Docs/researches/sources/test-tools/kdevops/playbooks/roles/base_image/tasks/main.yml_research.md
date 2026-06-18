# sources/test-tools/kdevops/playbooks/roles/base_image/tasks/main.yml

This entry point decides whether to create a base image. It stats `base_image_pathname`, includes `custom-image.yml` when `guestfs_has_custom_raw_image` is true, and includes `base-image.yml` only when the target image does not already exist and no custom raw image is configured.

Important APIs are `stat` and `include_tasks`. State is the existence check result and the base image file created by the included path. Integration depends on defaults and higher-level guestfs configuration selecting custom versus virt-builder generation. Risks include skipping regeneration whenever a stale image exists, unconditional custom-image execution regardless of whether `base_image_pathname` already exists, and no checksum or metadata validation on existing base images. Test signals should verify all three branches: existing normal image, missing normal image, and custom image configuration.
