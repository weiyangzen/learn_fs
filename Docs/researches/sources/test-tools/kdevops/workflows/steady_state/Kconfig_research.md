<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/steady_state/Kconfig -->
# sources/test-tools/kdevops/workflows/steady_state/Kconfig

## Purpose
This Kconfig file defines tunables for SSD steady-state preconditioning and fio steady-state verification. It captures target device selection, prefill workload shape, runtime, and steady-state pass criteria.

## Important Symbols
`SSD_STEADY_STATE_DEVICE` selects a default block device based on provider and storage type. Prefill controls include blocksize, iodepth, numjobs, loop count, verbose mode, maximum size, physical block size override, ioengine, direct I/O, allocation size, and extra fio arguments. Verification controls include runtime and IOPS/BW mean and slope limits plus required durations.

## Control Flow and Integration
All symbols are emitted to YAML for Ansible consumption. The Makefile targets call `playbooks/steady_state.yml` with tags for setup, prefill, and steady-state phases. Runtime logic in Ansible or helper scripts computes an effective blocksize when the config value is empty.

## State, Persistence, and Dependencies
Persistent configuration lands in generated kdevops vars. Runtime state is destructive or performance-sensitive because the selected device is prefilled. Dependencies include provider-specific device naming, fio, and the steady-state playbook.

## Risks and Test Signals
The workflow can overwrite the configured device, so defaults and user overrides require care. Device names vary by cloud and libvirt bus. Very long defaults such as `6h` runtime and multi-hour steady-state durations make test cycles expensive. Strong signals are generated fio commands, prefill logs, and steady-state criteria results.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/steady_state/Kconfig -->
