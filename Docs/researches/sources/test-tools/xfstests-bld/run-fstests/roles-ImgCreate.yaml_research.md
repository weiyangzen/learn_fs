# sources/test-tools/xfstests-bld/run-fstests/roles-ImgCreate.yaml

Purpose: custom Google Cloud IAM role for VMs that create/export/import/copy xfstests images.

Important permissions: compute disk create/delete/snapshot/use, image create/delete/deprecate/get/list/setLabels/update/useReadOnly, instance attach/detach/stop/update/use, network/subnetwork use, serviceAccount actAs, logging operations, resource manager project get, and storage object create/get/list/update.

Control flow/state: declarative role file applied to GCP IAM. Persistent effect is a custom role with ALPHA stage.

Dependencies/integration: used by image creation/export tooling referenced by `gce-xfstests create-image`, `export-image`, `import-image`, and `copy-image`.

Risks: broad compute and logging permissions, though more image-focused than LTM/KCS. It lacks `storage.objects.delete`, which may be intentional for image creator safety. ALPHA stage signals role instability.

Test signals: image creation pipeline should validate the exact role can create disks/images, upload objects, and complete without owner/editor privileges.
