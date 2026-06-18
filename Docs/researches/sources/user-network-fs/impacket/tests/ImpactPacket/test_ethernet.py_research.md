# sources/user-network-fs/impacket/tests/ImpactPacket/test_ethernet.py

## Purpose

`test_ethernet.py` validates Ethernet frame parsing and manipulation, with emphasis on 802.1Q/QinQ VLAN tag behavior.

## Important APIs, Types, And Functions

It imports `unittest`, `array`, `Ethernet`, and `EthernetTag`. `TestEthernet.setUp()` parses a VLAN-tagged frame. Tests cover basic getters/setters, `EthernetTag` getters/setters, and tag stack operations through `push_tag()`, `pop_tag()`, `get_tag()`, and `set_tag()`.

## Control Flow

The tests assert original frame fields, mutate ethertype and MACs, inspect and mutate VLAN tag fields, push S-tags and QinQ tags, verify tag counts/header sizes, test negative indices and out-of-range `IndexError`, reconstruct from serialized bytes, and remove a middle tag.

## State And Persistence Behavior

State is local Ethernet and tag objects. There is no persistence.

## Dependencies And Integration Points

It exercises `ImpactPacket.Ethernet`, `EthernetTag`, byte serialization, MAC storage as arrays, and VLAN tag stack behavior.

## Risks And Edge Cases

It does not test untagged frames, malformed short frames, payload preservation beyond ethertype, all provider-bridging variants, or invalid VLAN field ranges.

## Test Signals

Passing tests signal stable VLAN parsing, insertion/removal, indexing, header size updates, and Ethernet field mutation.
