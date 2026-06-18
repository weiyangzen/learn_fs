<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/do-reboot.yml -->
# sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/do-reboot.yml

Purpose: executes one reboot iteration in single-mode reboot-limit testing, supporting Ansible reboot, `systemctl reboot`, and `systemctl kexec`.

Important APIs/types/functions: modules `ansible.builtin.debug`, `ansible.builtin.file`, `ansible.builtin.reboot`, `ansible.builtin.command`, `ansible.builtin.stat`, `ansible.builtin.set_fact`, `ansible.builtin.slurp`, `ansible.builtin.shell`; variables/facts `var`, `become_method`, `post_reboot_delay`, `msg`, `reboot_command`, `reboot_timeout`, `loop_var`, `kexec_kernel_path`, `kexec_initrd_path`, `reboot_limit_count`; tasks `Print uname for each host`, `Hint to our watchdog our reboot-limit tests are about to kick off`, `Run the reboot test using the ansible reboot module`, `Reboot using systemctl reboot with proper handling`, `Get current kernel version for kexec`.

Control flow: Touches a local watchdog marker, performs the selected reboot method, loads kexec kernel/initrd and cmdline when requested, reads/increments boot count, optionally triggers sysrq crash on configured intervals, writes count, waits for system boot completion, and appends `systemd-analyze` output.

State and persistence behavior: Mutates host uptime, boot count file, optional kexec loaded kernel, sysrq state, and analyze log.

Dependencies and integration points: Included by main loop. Depends on kernel images/initrds, kexec-tools for kexec mode, systemd, and Ansible reconnection.

Risks: Crash injection is destructive. Kexec path selection uses the first existing candidate and fails if none found. Count writes only update existing files in one branch and create on first run.

Test signals: Signals are host returns, count increments, analyze lines appended, and expected crash behavior under crash settings.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/do-reboot.yml -->
