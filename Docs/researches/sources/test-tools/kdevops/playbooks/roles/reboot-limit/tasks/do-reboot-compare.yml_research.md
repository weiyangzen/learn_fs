<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/do-reboot-compare.yml -->
# sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/do-reboot-compare.yml

Purpose: runs paired regular and kexec reboot iterations for comparison mode.

Important APIs/types/functions: modules `ansible.builtin.debug`, `ansible.builtin.file`, `ansible.builtin.reboot`, `ansible.builtin.include_tasks`, `ansible.builtin.command`, `ansible.builtin.stat`, `ansible.builtin.set_fact`, `ansible.builtin.slurp`; variables/facts `var`, `msg`, `become_method`, `post_reboot_delay`, `reboot_type`, `data_path`, `loop_var`, `kexec_kernel_path`, `kexec_initrd_path`, `reboot_command`; tasks `Print uname for each host`, `Hint to our watchdog our reboot-limit comparison tests are about to kick off`, `Starting Phase 1 - Regular reboot test ({{ reboot_num }} of {{ reboot_limit_max }})`, `Run the regular reboot test using the ansible reboot module`, `Handle regular reboot count and data collection`.

Control flow: Switches facts and paths for regular reboot, includes reboot execution, then switches to kexec paths/type and includes reboot execution again for the same loop iteration.

State and persistence behavior: Persists separate regular and kexec count/analyze logs under comparison directories.

Dependencies and integration points: Included by reboot-limit main when comparison mode is enabled.

Risks: Fact switching must be correct or results can be mixed between modes. Each loop performs two disruptive reboots.

Test signals: Signals are separate count files advancing equally and separate analyze logs populated.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/do-reboot-compare.yml -->
