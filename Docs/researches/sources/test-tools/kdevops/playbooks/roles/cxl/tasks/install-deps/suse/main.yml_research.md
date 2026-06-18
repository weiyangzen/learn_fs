<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/suse/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/suse/main.yml

Source read: complete file, 83 lines, 2630 bytes, sha256 `5df178e38ecbb149`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/suse/main.yml_research.md`.

Purpose: SUSE-family build dependency installation for ndctl/cxl with old SLE repo gating.

Important APIs/types/functions: `set_fact` for distro/service-pack flags and `community.general.zypper` installing git-core, meson, gcc, pkg-config, uuid/kmod/udev/json-c/asciidoctor/keyutils/iniparser/bash-completion/jq/traceevent/tracefs packages with `replacefiles: true`.

Control flow: classify SUSE variant and SLE versions; default repos present; disable repos for SLE10/SLE11; install dependency list when repos are present.

State and persistence behavior: records facts and changes zypper package state.

Dependencies and integration: prepares ndctl build for SUSE systems in the CXL workflow.

Risks: ruby/asciidoctor package name is version-specific (`ruby3.1-rubygem-asciidoctor`). Older SLE skips deps but later ndctl build tasks may still execute and fail.

Test signals: Leap/Tumbleweed/SLE15 should install dependencies and pass ndctl Meson setup; SLE10/11 should be treated as unsupported before build.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/cxl/tasks/install-deps/suse/main.yml -->
