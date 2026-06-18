## sources/user-network-fs/nfs-utils/utils/statd/simulate.c

Purpose: Optional simulator CLI for exercising statd NSM procedures and receiving simulated callbacks.

Important APIs/types/functions: `simulator` dispatches to `simulate_mon`, `simulate_unmon`, `simulate_unmon_all`, `simulate_stat`, `simulate_crash`, and `daemon_simulator`; callback service `sim_sm_mon_1_svc` logs received status.

Control flow: Depending on argument count and command, it creates UDP RPC clients to target statd, sends NSM calls, and for `mon` registers a temporary simulator RPC service to wait for callback.

State and persistence: Uses a computed `sim_port` and rpcbind registration. No persistent state.

Dependencies and integration: Requires `SIMULATIONS`, generated `sim_sm_inter` RPC stubs, rpcbind, and statd service stubs.

Risks and test signals: It contains developer-era rough edges and abrupt fatal logging. Test only in simulation builds; verify pmap registration cleanup, monitor callback receipt, and all command argument forms.
