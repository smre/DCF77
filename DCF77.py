from datetime import datetime, timedelta
from pytz import timezone
import pytz
import math
import pyaudio
import numpy as np
import signal
import sys

# Signal timezone (Default is Europe/Berlin UTC+1)
signal_timezone = 'Europe/Berlin'


# Convert int to DCF77 compatible binary string
def to_binary(value, size):
    binary_value = '{0:b}'.format(int(value))
    return binary_value[::-1] + ('0' * (size - len(binary_value)))


# Convert int to BCD
def bcd(value, size):
    if size <= 4:
        return to_binary(value, size)
    else:
        ones = to_binary(math.floor(value % 10), 4)
        tens = to_binary(math.floor(value / 10), size - 4)
        return ones + tens


# Calculate even parity bit
def even_parity(value):
    return str(value.count('1') % 2)


# Is it DST?
def is_dst(tzone):
    tz = pytz.timezone(tzone)
    now = pytz.utc.localize(datetime.utcnow())
    return now.astimezone(tz).dst() != timedelta(0)


# Add n minutes to time
def add_minutes(time, minutes):
    return time + timedelta(minutes=minutes)


# Generate one minute string
def generate_minute(time):
    global signal_timezone

    # first 17 "useless" bits
    minute = '0' * 17

    # DST data
    minute += str(int(is_dst(signal_timezone)))
    minute += str(int(not is_dst(signal_timezone)))

    # start time code
    minute += '01'

    # minutes + parity bit
    minute += bcd(time.minute, 7)
    minute += even_parity(bcd(time.minute, 7))

    # hours + parity bit
    minute += bcd(time.hour, 6)
    minute += even_parity(bcd(time.hour, 6))

    # day of month
    minute += bcd(time.day, 6)

    # day of week
    minute += bcd(time.weekday() + 1, 3)

    # month number
    minute += bcd(time.month, 5)

    # year (within century) + parity bit for all date bits
    minute += bcd(time.year - 2000, 8)
    minute += even_parity(bcd(time.day, 6) + bcd(time.weekday() + 1, 3) + bcd(time.month, 5) + bcd(time.year - 2000, 8))

    # special "59th" second (no amplitude modulation)
    minute += '-'

    return minute


# Generate 11 minutes of DCF77 signal
def generate_bits():
    global signal_timezone
    bits = ''

    # Get signal timezone time
    zero_date = pytz.utc.localize(datetime.utcnow())
    signal_tz = timezone(signal_timezone)
    time = zero_date.astimezone(signal_tz)

    for i in range(1, 12):
        bits += generate_minute(add_minutes(time, i))

    return bits


# Generate a sine wave
def sine(frequency, length, rate, strength):
    length = int(length * rate)
    factor = float(frequency) * (math.pi * 2) / rate
    return np.sin(np.arange(length) * factor) * strength


# Play a tone
def play_tone(chunks, stream):
    # Distort the signal
    chunk = np.concatenate(chunks) * 32767
    chunk = np.floor(chunk) / 32767
    stream.write(chunk.astype(np.float32).tostring())


# Generate a tone
def generate_tone(input):
    chunks = []
    t = datetime.now()
    code = input[t.second:]
    frequency = 15500
    rate = 44100
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=rate, output=1)

    for c in code:
        if c == "1":
            chunks.append(sine(frequency, 0.2, rate, 0.5))
            chunks.append(sine(frequency, 0.8, rate, 1.0))
        elif c == "0":
            chunks.append(sine(frequency, 0.1, rate, 0.5))
            chunks.append(sine(frequency, 0.9, rate, 1.0))
        elif c == "-":
            # special "59th" second. No amplitude modulation.
            chunks.append(sine(frequency, 1.0, rate, 1.0))

        play_tone(chunks, stream)
        chunks = []

    stream.close()
    p.terminate()


# Handle Ctrl + C
def sigint_handler(signal, frame):
    print '\nInterrupted'
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)

    seq = generate_bits()

    # Time generate_tone to the start of next second
    start_time = datetime.now()
    while start_time.second == datetime.now().second:
        pass

    print 'Transmitting DCF77 signal ({})\nPress Ctrl + C to stop.'.format(signal_timezone)
    generate_tone(seq)
    print 'Transmission finished.'
