<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/cxl-create-dc-region/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/cxl/tasks/cxl-create-dc-region/main.yml

Source read: complete file, 20 lines, 1041 bytes, sha256 `94c45a6e7e8721f1`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/cxl/tasks/cxl-create-dc-region/main.yml_research.md`.

Purpose: create a CXL dynamic-capacity region through sysfs before adding dynamic capacity extents.

Important APIs/types/functions: privileged `ansible.builtin.shell` writing to `/sys/bus/cxl/devices/...` files, `cxl list -uR`, and debug output.

Control flow: write `create_dc_region`, configure interleave granularity/ways, set decoder mode `dc0`, set DPA and region size, bind target, commit the region, bind it to the CXL region driver, then display `cxl list -uR`.

State and persistence behavior: mutates live kernel CXL sysfs state by creating and binding a region. This is runtime hardware/VM state, not a config file.

Dependencies and integration: included from `cxl/tasks/main.yml` when `kdevops_enable_cxl_dcd` is true. Assumes decoder names `decoder0.0` and `decoder2.0` and available cxl CLI.

Risks: hard-coded sysfs paths, sizes, region id, and decoder topology make this fragile across QEMU/kernel versions. The long shell string has no `set -e`, so partial failures may go unnoticed.

Test signals: `cxl list -uR` should show a committed DC region with the expected size/target; sysfs writes should fail loudly in negative topology tests.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/cxl-create-dc-region/main.yml -->
