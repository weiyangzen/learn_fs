# File Research: sources/os/bsd/netbsd-src/sys/sys/midiio.h

Defines MIDI and sequencer ioctl/event ABI compatible with OSS at the byte level. It includes MPU command records, `/dev/midi` ioctls, sequencer/timer ioctls, synth info structures, MIDI controller/status constants, RPN and pitch constants, old sequencer command values, native 8-byte `seq_event_t` union layouts, event-construction macros, sysex/instrument patch structures, and userland/kernel pitch-to-frequency conversion helpers.

The header is mostly ABI and macro logic. Risks are binary compatibility with OSS event byte layouts, endian-dependent patch/time-signature fields, packed union layout, and documented quirks around controller changes and partially unimplemented sequencer events.
