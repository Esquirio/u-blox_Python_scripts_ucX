# Flash NINA Firmware

This script is used to flash firmware onto u-blox NINA modules via serial communication. It reads configuration parameters from a configuration file and a JSON file, sends AT commands to the module, and performs the firmware flashing process using the XMODEM protocol.

## Prerequisites

- Python 3.6 or higher
- Required Python packages:
  - `pyserial`
  - `tqdm`
  - `xmodem`
  - `colorama`

## Configuration

Create a configuration file or use the `config.txt` available in the repo. The config file should have the following format:

See the following example:
```
MODULE="NINA-W15X"
FW_VERSION="6.0.1"
COMPORT=COM179
BAUDRATE=921600
```

> [!NOTE]  
> This file should be in the same directory as the script `flash_NINA_firmware.py`.

## Firmware Directory Structure

The firmware files and their corresponding JSON files should be organized in the `Firmwares` directory. The JSON file should follow the naming convention `<MODULE>-<FW_VERSION>.json`. Here is an example of the directory structure:

```
flash_u-blox_modules/
├── flash_NINA_firmware.py
├── config.txt
├── Firmwares/
│   ├── NINA-W22X
│   ├── NINA-W13X
│   ├── NINA-B15X
|       |── NINA-W15X-5.0.0
|       |── NINA-W15X-5.2.2
|       |── NINA-W15X-6.0.1
|           |── NINA-W15X-CF-1.0.json
|           |── NINA-W15X-SI-6.0.1-001.txt
|           |── NINA-W15X-SW-6.0.1-001.bin
```

## Usage

On the console, run the following command to execute the script:
```
python flash_NINA_firmware.py -f config.txt
```

### Video

Watch the video below to see how the script works.

<video src="media/how_to_use_the_script.mp4" width="960" height="540" controls></video>