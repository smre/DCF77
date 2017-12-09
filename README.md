# DCF77.py

Python script that transmits a faux [DCF77](https://en.wikipedia.org/wiki/DCF77) signal. It uses system time as its time source. It can be used to time radio controlled clocks and watches that accept DCF77 signal. Requires [PyAudio](http://people.csail.mit.edu/hubert/pyaudio/) and [NumPy](http://www.numpy.org/) to run.

This script was tested on my Casio Wave Ceptor wristwatch.

#### Signal documentation
* [https://en.wikipedia.org/wiki/DCF77](https://en.wikipedia.org/wiki/DCF77)

### Disclaimer
* __This script will produce a high-pitched 15.5kHz sine wave noise! Please protect your hearing! Also, it may or may not be legal to transmit this sound in your country. Consult your local laws if you are unsure.__

### Instructions

1. Run the script. The sound will start playing immediately. The encoded time signal will automatically be in German time (UTC+1)<sup>__1__</sup>.
2. Set your radio controlled watch or clock to "receive" mode and place its antenna near the speaker or headphones (~1-5 cm)
3. Wait. It can take anywhere from 2 to 10 minutes for your watch to synchronize. This script will produce 10-11 minutes of DCF77 signal before closing. You can terminate the script yourself by pressing <kbd>Ctrl</kbd> + <kbd>C</kbd>.

<sup>__1__</sup> To change the signal timezone, edit [line 11](https://github.com/smre/DCF77/blob/6e250097d081fec1db9d0723db5563f866729d30/DCF77.py#L11) in the script.

### What if it doesn't work?

It's most likely one of these reasons:

1. __The speaker volume is not loud enough:__ Try increasing your system volume.
2. __The clock/watch is not placed near enough to the speaker:__ Try placing it closer to the speaker.

If it's still not working, your clock/watch probably cannot be fooled by this signal.
