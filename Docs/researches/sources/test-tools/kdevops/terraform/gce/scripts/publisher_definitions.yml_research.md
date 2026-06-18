# sources/test-tools/kdevops/terraform/gce/scripts/publisher_definitions.yml

Purpose: YAML catalog of Linux image publishers for GCE image Kconfig generation. Each top-level key names a distribution family such as `debian`, `ubuntu`, `redhat`, or `rocky`.

The schema provides `project_id`, `publisher_name`, `description`, `priority`, `default_disk_size`, and `family_patterns`. Generator scripts can use this to enumerate public image projects, match image families by regex, order menus, and choose sensible boot disk defaults.

There is no executable control flow or persistence in this file; it is read as configuration by provider scripts. Its integration points are GCE public image projects and generated Kconfig image menus. The comments document update workflow through `gcloud compute images list` and regeneration of `Kconfig.image`.

Risks are data freshness and regex breadth. Broad patterns such as `ubuntu-.*` or `centos-.*` are convenient but can match deprecated or unexpected families unless the consuming script filters further. Test signals should validate YAML parsing, required keys for every publisher, unique priorities or deterministic ordering, and that family regexes match representative live or fixture image-family names.
