# File Research: sources/os/bsd/netbsd-src/lib/libossaudio/oss4_mixer.c

Implements OSSv4 audio and mixer ioctl compatibility. It synthesizes `oss_audioinfo`, `oss_card_info`, `oss_sysinfo`, `oss_mixerinfo`, `oss_mixext`, enum info, and mixer values from NetBSD `/dev/audioN`, `/dev/mixerN`, and `AUDIO_*` ioctls.

The code opens device nodes on demand, reports a fake OSS product/version, converts NetBSD mixer classes to OSS root/group controls, maps NetBSD enum/set/value controls to OSS enum/slider/mute types, and reads/writes controls by translating OSS control numbers to NetBSD mixer indices offset by one.

Notable behavior: NetBSD has no separate exclusive hardware engine path, so `SNDCTL_AUDIOINFO_EX` aliases normal audio info. NetBSD set controls are exposed as single-choice enums because real OSS software is assumed not to support `MIXT_ENUM_MULTI`.
