ToneTutorLib: 
A python3 library providing audio processing, characteristic generation, and 
tone recognition for ToneTutor decoupled from a specific data source.

Dependencies:
 - normalization: scipy, numpy (for scipy), sndhdr, taglib, mutagen, tkSnack, Tkinter (for tkSnack).
 - normalization dependency 'taglib' requires system-level taglib.
 - normalization depends on system-level utility 'normalize-audio'.
 - a few characteristics depend on tkSnack which was written for python 2.7.  The version
    included with this package makes some small changes for python 3 compatibility.


This package provides three essential services; audio normalization, characteristic generation
    and tone recognition.

Audio normalization takes recorded audio and converts it to a standard form, performing 
operations such as removing silence and setting a standard volume.

Characteristic generation takes normalized audio and generates a number of different
characteristics to quantify the qualities of that audio.  Examples include maximum volume
or prevalent frequency for each 1/8th of the sample.

Tone recognition provides a tone based on the characteristics of an audio sample.

Typical Usage:
    from ttlib.normalization.interface import normalize_pipeline
    from ttlib.characteristics.interface import generate_all_characteristics
    from ttlib.recognizer import ToneRecognizer

    normalized_audio_path = '/path/to/normalized_audio_sample.mp3'
    normalize_pipeline('/path/to/audio_sample.mp3', normalized_audio_path)
    sample_rate, wave_data = scipy.io.wavfile.read(normalized_sample_path)
    sample_characteristics = generate_all_characteristics(wave_data, sample_rate)

    tr = ToneRecognizer()
    tone = tr.get_tone(sample_characteristics)
