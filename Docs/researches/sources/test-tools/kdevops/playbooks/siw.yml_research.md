# sources/test-tools/kdevops/playbooks/siw.yml

Purpose: wrapper playbook for software-emulated iWARP RDMA over TCP/IP setup.

Important APIs/types/functions: targets `baseline:dev` and invokes role `siw`.

Control flow: host selection then role execution.

State/persistence behavior: delegated to `siw`, likely udev/module/network changes.

Dependencies/integration: integrates with RDMA testing workflows.

Risks/test signals: wrapper risk is limited to host/role naming. Test signal is successful role execution and siw interface/module state.
