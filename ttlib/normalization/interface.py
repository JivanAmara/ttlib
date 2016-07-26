'''
Created on Jul 14, 2016

@author: jivan
'''
import os
import shutil
import scipy.io.wavfile
from tempfile import NamedTemporaryFile
import sndhdr
import taglib
import mutagen.mp3
from subprocess import Popen
from logging import getLogger
from tkinter import Tk
from tkSnack3 import initializeSnack, Sound

root = Tk()
initializeSnack(root)

logger = getLogger(__name__)


def normalize_pipeline(audio_sample_path, normalized_audio_path):
    ''' | *brief*: Creates a normalized wav file for the file located at *audio_sample_path*.
        | *return*: Absolute path to the new normalized file.
    '''
    with open(audio_sample_path, 'rb') as f:
        wav_file = NamedTemporaryFile(suffix='.wav', delete=False)
        normal_volume_wav = NamedTemporaryFile(suffix='.wav', delete=False)

        convert_wav(audio_sample_path, wav_file.name)
        normalize_volume(wav_file.name, normal_volume_wav.name)
        strip_silence(normal_volume_wav.name, normalized_audio_path)

        if wav_file:
            os.unlink(wav_file.name)
        if normal_volume_wav:
            os.unlink(normal_volume_wav.name)

def convert_wav(infile_path, outfile_path):
    ''' *brief*: Converts *infile_path* to a single channel wav file with sampling rate of 44100
            and writes the result to *outfile_path*.
    '''
    extension, sample_rate, audio_length = get_file_metadata(infile_path)
    if extension is None:
        raise Exception('infile_path has invalid audio extension')

    if extension == 'wav' and sample_rate == 44100:
        shutil.copy(infile_path, outfile_path)
    else:
        # -ac is audio channel count
        # -ar is audio sample rate
        cmd = [
            'avconv', '-y', '-i', infile_path,
            '-ac', '1', '-ar', '44100', outfile_path
        ]
        import sys
        with open(os.devnull) as nullfile:
#             p = Popen(cmd, stdout=nullfile, stderr=nullfile)
            p = Popen(cmd, stdout=sys.stdout, stderr=sys.stdout)

        p.wait()
        if p.returncode != 0:
            msg = '\nretcode {} for:\n{}'.format(p.returncode, ' '.join(cmd))
            logger.error(msg)
            raise Exception(msg)

def normalize_volume(infile_path, outfile_path):
    ''' *brief*: Uses command-line tool 'normalize-audio' to normalize the volume of *infile_path*
            and writing the normalized audio to *outfile_path*
    '''
    try:
        shutil.copyfile(infile_path, outfile_path)
        cmd = ['normalize-audio', '-q', outfile_path]
        p = Popen(cmd)
        p.wait()
        if p.returncode != 0:
            msg = 'Non-zero return code {} from {}'.format(p.returncode, cmd)
            logger.error(msg)
            raise Exception(msg)
    except:
        os.unlink(outfile_path)
        raise

def strip_silence(infile_path, outfile_path):
    try:
        s = Sound()
        s.load(infile_path)

        pitches = s.pitch()
        if pitches is None:
            return None

        sample_count = s.length()

        # Determine the segments of continuous non-zero pitch as 2-tuples (start-idx, end-idx)
        nonzero_segments = []
        start = None
        end = None
        for i, p in enumerate(pitches):
            if start is None and p == 0.0:
                continue
            elif start is None and p != 0.0:
                start = i
            elif start is not None and p == 0.0:
                end = i - 1
                nonzero_segments.append((start, end))
                start = None
                end = None
                continue
            elif start is not None and i == (len(pitches) - 1):
                end = i
                nonzero_segments.append((start, end))

        # Determine the longest segment and cut the sound to only include those samples
        longest_segment = (0, 0)
        for nzs in nonzero_segments:
            if nzs[1] - nzs[0] > longest_segment[1] - longest_segment[0]:
                longest_segment = nzs
        samples_per_pitch_value = sample_count / float(len(pitches))
        longest_segment_in_samples = (
            int(samples_per_pitch_value * longest_segment[0]),
            int(samples_per_pitch_value * longest_segment[1])
        )

        # If there's nothing left, raise an exception
        if longest_segment_in_samples[1] - longest_segment_in_samples[0] == 0:
            raise('No data left after stripping')
        # We're good to go, write the trimmed audio.
        else:
            s.cut(longest_segment_in_samples[1], sample_count - 1)
            s.cut(0, longest_segment_in_samples[0])

            s.write(outfile_path)
    finally:
        # tkSnack is a c library and the memory it uses won't get garbage collected.
        # Release the memory it's using with this.
        try:
            s.destroy()
        except:
            pass

def get_file_metadata(filepath):
    """ *brief*: Returns the file extension, sample rate, and audio length for the audio file located at
            *filepath*.
    """
    try:
        file_extension = filepath.split('.')[:-1]
    except IndexError:
        file_extension = None

    audio_details = sndhdr.whathdr(filepath)

    if audio_details:
        (type, sample_rate, channels, frames, bits_per_sample) = audio_details
        audio_metadata = (file_extension, sample_rate, None)
    else:
        try:
            tlinfo = taglib.File(filepath)
            sample_rate = tlinfo.sampleRate
        except OSError:
            sample_rate = None

        try:
            audio = mutagen.mp3.MP3(filepath)
            audio_length = audio.info.length
        except mutagen.mp3.HeaderNotFoundError:
            audio_length = None
        audio_metadata = (file_extension, sample_rate, audio_length)

    return audio_metadata

