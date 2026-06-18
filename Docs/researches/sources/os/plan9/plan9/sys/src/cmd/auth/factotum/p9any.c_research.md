# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/p9any.c

Implements the `p9any` protocol negotiator. Its negotiable protocol list contains `p9sk1`; it exchanges `proto@domain` offerings and then relays to a selected subprotocol.

Client flow reads server protocol list, selects a matching key/protocol/domain, writes `proto dom`, optionally waits for `OK` in version 2, then relays read/write calls to the subprotocol. Server flow advertises available `p9sk1@dom` keys, receives client selection, initializes the subprotocol, optionally returns `OK`, then relays.

`passret` propagates subprotocol return states, authinfo, needkey strings, confirmation requests, and toosmall sizes to the outer `Fsstate`. This file is a wrapper state machine around `p9sk1`, with careful ownership of `subfss` and shared attrs.
