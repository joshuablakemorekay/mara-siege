"""
Sounds - every sound effect is generated in code, so there are no audio files
Temple bells, singing bowls and soft taps to match the garden theme
"""

import math
import random
from array import array
import pygame

SAMPLE_RATE = 22050

_sounds = {}
_last_played = {}
_muted = False
_channels = 1

# Shortest gap between repeats, so rapid fire doesn't turn into noise
MIN_GAP = {'shoot': 0.09, 'pop': 0.06, 'breach': 0.15}


def _tone(partials, duration, decay, volume, noise=0.0):
    """Build a sound from (frequency, loudness) pairs that fade out over time"""
    count = int(SAMPLE_RATE * duration)
    rng = random.Random(1)
    samples = array('h')
    for i in range(count):
        t = i / SAMPLE_RATE
        envelope = math.exp(-t * decay) * min(1.0, t * 400)  # Quick fade in, then fade out
        value = sum(level * math.sin(2 * math.pi * freq * t) for freq, level in partials)
        if noise:
            value += noise * (rng.random() * 2 - 1)
        sample = int(max(-1.0, min(1.0, value * envelope * volume)) * 32767)
        for _ in range(_channels):
            samples.append(sample)
    return pygame.mixer.Sound(buffer=samples.tobytes())


def _join(*parts):
    """Play several notes one after another as a single sound"""
    samples = array('h')
    for part in parts:
        samples.frombytes(part.get_raw())
    return pygame.mixer.Sound(buffer=samples.tobytes())


def init():
    """Create all the sounds - safe to call even if there is no audio device"""
    global _channels, SAMPLE_RATE
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(SAMPLE_RATE, -16, 1, 512)
        SAMPLE_RATE, _, _channels = pygame.mixer.get_init()
    except pygame.error:
        return  # No audio available - the game runs silently

    _sounds['shoot'] = _tone([(880, 1.0)], 0.07, 45, 0.12)
    _sounds['pop'] = _tone([(330, 0.6), (165, 0.4)], 0.12, 30, 0.25, noise=0.3)
    _sounds['place'] = _tone([(196, 1.0), (392, 0.3)], 0.15, 28, 0.35, noise=0.15)  # Wooden knock
    _sounds['error'] = _tone([(140, 1.0), (147, 0.8)], 0.18, 12, 0.2)
    _sounds['breach'] = _tone([(60, 1.0), (90, 0.5)], 0.4, 9, 0.6, noise=0.1)  # Low thud
    _sounds['sell'] = _join(_tone([(660, 1.0)], 0.1, 20, 0.25), _tone([(440, 1.0)], 0.18, 15, 0.25))
    _sounds['upgrade'] = _join(_tone([(523, 1.0)], 0.1, 20, 0.25), _tone([(784, 1.0)], 0.22, 12, 0.25))
    # Temple bell - the uneven overtones are what make it sound like a bell
    _sounds['bell'] = _tone([(392, 1.0), (392 * 2.76, 0.4), (392 * 5.4, 0.2)], 2.0, 2.2, 0.3)
    # Deep gong for boss waves - two close notes give it a slow wobble
    _sounds['gong'] = _tone([(73, 1.0), (75, 0.8), (73 * 2.3, 0.4), (73 * 4.1, 0.2)], 3.0, 1.2, 0.55)
    # Singing bowl for abilities
    _sounds['bowl'] = _tone([(528, 1.0), (531, 0.8), (528 * 2.7, 0.25)], 2.2, 1.6, 0.3)
    _sounds['victory'] = _join(*[_tone([(f, 1.0), (f * 2.76, 0.3)], 0.35, 6, 0.3)
                                 for f in (392, 494, 587, 784)])
    _sounds['defeat'] = _join(*[_tone([(f, 1.0), (f * 1.5, 0.3)], 0.5, 5, 0.35)
                                for f in (220, 185, 147)])


def play(name):
    """Play a sound by name (does nothing if muted or audio is unavailable)"""
    if _muted or name not in _sounds:
        return
    now = pygame.time.get_ticks() / 1000
    if now - _last_played.get(name, -10) < MIN_GAP.get(name, 0):
        return
    _last_played[name] = now
    _sounds[name].play()


def toggle_mute():
    """Switch sound on/off - returns True if now muted"""
    global _muted
    _muted = not _muted
    if _muted and pygame.mixer.get_init():
        pygame.mixer.stop()  # Cut off anything still ringing
    return _muted
