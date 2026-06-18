<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/suse/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/suse/main.yml

Source read: complete file, 66 lines, 2257 bytes, sha256 `df1a68af45e6ed86`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/suse/main.yml_research.md`.

Purpose: SUSE-family filesystem tool dependency setup with legacy SLE repo gating.

Important APIs/types/functions: `set_fact` for SUSE family/version flags and `ansible.builtin.package` installing `xfsprogs`, `e2fsprogs`, and `btrfsprogs` when `repos_present`.

Control flow: classify SLE/Leap/Tumbleweed; set detailed SLE service-pack booleans; clear them on non-SLE; default `repos_present=true`; set it false for SLE10/SLE11; install packages only if repos are present.

State and persistence behavior: records distro facts and changes package state on supported SUSE releases.

Dependencies and integration: mirrors SUSE gating used in other roles and feeds `create_partition`.

Risks: old SLE systems skip package installation but later partition tasks may still run and fail. Package name is `btrfsprogs`, not `btrfs-progs`, which is correct for some SUSE releases but version-sensitive.

Test signals: verify SLE10/11 skip behavior; Leap/Tumbleweed/SLE15 should install mkfs tooling.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_partition/tasks/install-deps/suse/main.yml -->
