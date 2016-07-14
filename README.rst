ToneTutorLib: 
A python3 library providing audio processing, characteristic generation, and 
tone recognition for ToneTutor decoupled from a specific data source.

Dependencies:
 - normalization: scipy, sndhdr, taglib, mutagen, tkSnack, Tkinter (for tkSnack).
 - normalization dependency 'taglib' requires system-level taglib.
 - normalization depends on system-level utility 'normalize-audio'.


This package provides three essential services; audio normalization, characteristic generation
    and tone recognition.

Audio normalization takes recorded audio and converts it to a standard form, performing 
operations such as removing silence and setting a standard volume.

Characteristic generation takes normalized audio and generates a number of different
characteristics to quantify the qualities of that audio.  Examples include maximum volume
or prevalent frequency for each 1/8th of the sample.

Tone recognition provides a tone based on the characteristics of an audio sample.

Typical Usage:

    normalized_sample_path = normalize_pipeline('/path/to/audio_sample.mp3')
    sample_rate, wave_data = scipy.io.wavfile.read(normalized_sample_path)
    sample_characteristics = generate_all_characteristics(normalized_sample)
    tr = ToneRecognizer()
    tone = tr.get_tone(sample_characteristics)
