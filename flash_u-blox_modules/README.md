# Flash NINA firmware

Script to test the firmware update process for u-connectXpress.

## Getting started

Update the config.txt file with the required information. This file should be in the same directory of the of the scrip `flash_NINA_firmware.py`

See the following example:
```
COMPORT=COM58
BAUDRATE=115200
PATH="C:\Firmwares\NINA-W15X-5.0.0\NINA-W15X-CF-1.0.json"
```

Note: Add the complete path, including the JSON file name. This script was tested using a short path (50 characters or less) and no spaces or special characters.


On the console, run the following command to execute the script:
```
python flash_NINA_firmware.py -c config.txt
```

### Required Python packages

The Python packages list shown bellow is required to run this script:

- serial
- json
- argparse
- os
- time
- tqdm
- xmodem
- colorama

### Video

Watch the video below to see how the script work.

<video src="media/how_to_use_the_script.mp4" width="960" height="540" controls></video>