# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/httpattack.py

## Purpose
`httpattack.py` dispatches relayed HTTP/HTTPS sessions to specific HTTP-based attack mixins: AD CS certificate enrollment, SCCM policy secret retrieval, SCCM distribution point file dumping, or a minimal default root-page dump.

## Important APIs, Types, and Functions
- `PROTOCOL_ATTACK_CLASS = "HTTPAttack"` advertises the plugin.
- `HTTPAttack(ProtocolAttack, ADCSAttack, SCCMPoliciesAttack, SCCMDPAttack)` registers `PLUGIN_NAMES = ["HTTP", "HTTPS"]`.
- `run()` checks `config.isADCSAttack`, `config.isSCCMPoliciesAttack`, and `config.isSCCMDPAttack` to call the corresponding mixin `_run()`.

## Control Flow
When ntlmrelayx executes this attack, `run()` selects one configured mode in priority order: ADCS, SCCM policies, SCCM DP. If none are configured, it performs a GET `/`, prints the HTTP status/reason, reads the body, and prints it.

## State and Persistence Behavior
The dispatcher itself keeps no additional state. The selected mixin may write certificate files, SCCM loot directories, policies, or downloaded files. The default path only reads a response and prints to stdout.

## Dependencies and Integration Points
It depends on the attack base and HTTP mixins from `attacks/httpattacks`. It assumes `self.client` has `request()` and `getresponse()` methods compatible with `http.client`-style clients.

## Risks and Edge Cases
Only one attack mode runs because of `if/elif` ordering. The default branch prints raw response bodies directly and does not write deterministic loot. Misspelled config attributes would raise at runtime.

## Test Signals
Tests can use a fake client and config to assert dispatch order, request paths, and that each mode invokes the intended mixin method exactly once.
