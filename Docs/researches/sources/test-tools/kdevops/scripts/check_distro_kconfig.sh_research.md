# sources/test-tools/kdevops/scripts/check_distro_kconfig.sh

Purpose: placeholder Kconfig helper that always prints `n`.

Important APIs/types/functions: Bash stdout only.

Control flow: unconditional `echo n`.

State/persistence behavior: stateless.

Dependencies/integration: likely used where distro feature autodetection is not implemented.

Risks/test signals: always disables the queried feature. Test signal is stable `n` output.
