
# sources/user-network-fs/rclone/lib/buildinfo/arch.go

Purpose: reports runtime architecture details, especially ARM compatibility levels relevant to Go builds.

Important APIs/types/functions: `GetSupportedGOARM` inspects `runtime.GOARCH` and `golang.org/x/sys/cpu` ARM feature flags to return 7, 6, 5, or 0. `GetArch` returns `runtime.GOARCH` with explanatory ARM suffixes.

Control flow: if running 32-bit ARM with initialized CPU feature data, VFPv3 maps to GOARM 7, VFP to 6, and no VFP to 5. `GetArch` annotates `arm64` as ARMv8-compatible and `arm` based on supported GOARM.

State/persistence: no state.

Dependencies/integration: used by rclone build/version reporting to describe architecture. Depends on `runtime` and `x/sys/cpu`.

Risks: it reports CPU-supported GOARM, not necessarily the GOARM value used to build the binary, as comments explain. Non-ARM returns unannotated runtime architecture.

Test signals: no direct test in this subset; behavior is observable in build info output.
