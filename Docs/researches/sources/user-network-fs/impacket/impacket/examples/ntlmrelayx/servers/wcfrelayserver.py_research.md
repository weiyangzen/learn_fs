# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/wcfrelayserver.py

Purpose: implements a WCF/ADWS NetTcpBinding relay frontend. It parses .NET Message Framing and NegotiateStream records, relays NTLM negotiate/authenticate messages to a selected target protocol client, then either enqueues the resulting session for SOCKS or launches a configured attack.

Important APIs and control flow: `WCFRelayServer.WCFServer` is a threaded TCP server with IPv4/IPv6 binding via `get_address()`. `WCFHandler.handle()` validates Version, Mode, Via, KnownEncoding, and Upgrade records, requires `net.tcp://` and `application/negotiate`, then reads NegotiateStream handshake records. It unwraps SPNEGO or raw NTLM, calls `do_ntlm_negotiate()` to initialize the target client and get a challenge, sends the challenge back, receives NTLM authenticate, calls `do_ntlm_auth()`, logs and writes John hash material, registers target outcome, and calls `do_attack()`.

State and persistence: per-connection handler state includes selected target, protocol client, challenge message, auth user, and machine-account fields. Persistent side effects are optional hash output and target progress stored in `TargetsProcessor`.

Dependencies and integration: integrates with `TargetsProcessor`, protocol client classes in config, `activeConnections` for SOCKS, configured attack classes, NTLM/SPNEGO helpers, and SMB server hash formatting utilities.

Risks and test signals: `recvall()` can loop forever if the peer closes before enough bytes arrive. The parser supports only NetTcpBinding Negotiate. Tests should cover framing validation failures, SPNEGO unsupported mech negotiation, raw NTLM path, target exhaustion, remove-target AV pair handling, successful SOCKS enqueue, classic attack dispatch, hash output, and failed negotiate/auth target registration.
