# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_connections.py

## Purpose
This file tests node connection handler configuration, Tor/I2P provider validation, and privacy policy enforcement for Foolscap tub creation. It ensures Tahoe maps config settings to default handlers and rejects unsafe or invalid combinations.

## Important APIs, Types, And Functions
Test classes are `CreateConnectionHandlersTests`, `Tor`, `I2P`, `Connections`, and `Privacy`. They use `config_from_string`, `create_connection_handlers`, `create_main_tub`, `PrivacyError`, `create_tor_provider`, `create_i2p_provider`, Foolscap `tcp.DefaultTCP`, and test `ConstantAddresses`.

## Control Flow
Tests construct small config strings, create providers or handler maps, and assert returned dictionaries or raised `ValueError`/`PrivacyError`. Tor tests validate bad endpoint types and non-integer ports. I2P tests reject simultaneous `sam.port` and `launch`. Connection tests cover defaults, TCP-over-Tor, unavailable Tor import, unknown handler names, and disabled TCP. Privacy tests ensure `reveal-IP-address = false` rejects TCP defaults and AUTO tub locations unless TCP is disabled.

## State, Persistence, And Dependencies
There is no persistence. The tests depend on provider parser behavior, Foolscap connection handler classes, and node privacy checks.

## Risks And Test Signals
These tests catch high-impact privacy regressions: accidentally revealing IP addresses when privacy is requested, silently accepting unavailable Tor routing, or allowing invalid endpoint configuration. Exact error-message assertions also preserve user guidance.
