# sources/test-tools/syzkaller/dashboard/config/linux/bits/apparmor.yml

Purpose: selects AppArmor as the primary Linux security module for configs that fuzz AppArmor behavior.

Important keys: disables SELinux and Smack, enables `SECURITY_APPARMOR`, introspection policy on v5.19+, hashing/debug/assert options, `DEFAULT_SECURITY_APPARMOR`, and sets the `LSM` order string ending with AppArmor and BPF.

Control flow: declarative Kconfig fragment.

State and persistence: modifies generated kernel security module configuration.

Dependencies and integration points: Linux security module Kconfig, LSM ordering, syzkaller security-manager configurations.

Risks: LSM ordering is semantically important; missing a required LSM in the string can change boot/runtime behavior. Debug/assert options increase coverage but may affect performance and noise.

Test signals: generated kernels should boot with AppArmor as default security module and expose AppArmor policy/debug surfaces.
