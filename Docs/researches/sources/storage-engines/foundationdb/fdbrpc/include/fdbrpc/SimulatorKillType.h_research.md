## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/SimulatorKillType.h

Purpose: Defines the simulator fault/kill severity enum used by simulation policies and process/machine kill APIs.

Important APIs/types/functions: `simulator::KillType` includes `KillInstantly`, `InjectFaults`, `FailDisk`, `RebootAndDelete`, `RebootProcessAndDelete`, `RebootProcessAndSwitch`, `Reboot`, `RebootProcess`, and `None`.

Control flow: None in this header. The comment states enum order matters because simulation code compares kill types to rank destructiveness.

State and persistence behavior: No state. The enum is part of simulator API contracts and may appear in shutdown futures/signals.

Dependencies and integration points: Used by `simulator.h`, `SimulatorProcessInfo.h`, simulation policies, and fault injection logic.

Risks: Reordering enum values changes severity comparisons. Adding new values requires auditing policy comparison logic and trace/reporting code.

Test signals: Simulation policy tests that downgrade/compare kill types, process shutdown signal behavior, and coverage for every kill mode.
